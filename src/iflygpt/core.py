import os
from enum import Enum
from typing import List, Optional, Union

from httpx import AsyncClient, Client, Cookies

from iflygpt.exp import LoginError, AuthError, RequestError, APIConnectionError, IflyGPTError

from iflygpt.util import decode


class Method(Enum):
    GET = 'GET'
    POST = 'POST'


class ChatBot:
    def __init__(self, name):
        self.name = name

        self.__ifly_account = os.environ.get('IFLY_ACCOUNT')
        self.__ifly_pwd = os.environ.get('IFLY_PWD')

        gt_token_file = os.environ.get('GT_TOKEN_FILE')
        with open(gt_token_file, 'r') as f:
            self.__gt_token = f.read()

        self.__session = AsyncClient()
        self.__request_headers = {
            'Host': 'xinghuo.xfyun.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/113.0.0.0 Safari/537.36',
            'Origin': 'https://xinghuo.xfyun.cn',
            'Referer': 'https://xinghuo.xfyun.cn/desk'
        }
        self.__cookies = Cookies()

    @property
    def gt_token(self):
        return self.__gt_token

    def login(self) -> dict:
        url = 'https://sso.xfyun.cn/SSOService/login/check-account'
        headers = {
            'Host': 'sso.xfyun.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/113.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://passport.xfyun.cn',
            'Referer': 'https://passport.xfyun.cn'
        }
        data = {'accountName': self.__ifly_account, 'accountPwd': self.__ifly_pwd}

        # resp = await self.__session.post(url, headers=headers, data=data)
        with Client() as client:
            resp = client.post(url, headers=headers, data=data)
            if resp.status_code == 200:
                resp_json = resp.json()
                if resp_json['code'] == 0:
                    _data = resp_json['data']
                    self.__cookies.set('ssoSessionId', _data['ssoSessionId'])
                    self.__cookies.set('account_id', _data['account_id'])

                    return _data
                else:
                    raise LoginError(resp_json['desc'])

            else:
                raise LoginError(resp.text)

    async def get_chat_list(self) -> List[dict]:
        """
        获取会话列表
        :return：会话列表
        """

        url = 'https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/chat-list'

        return await self.__request(url, self.__request_headers, Method.GET)

    async def get_prompt_list(self) -> List[dict]:
        """
        获取提示列表
        :return：提示列表
        """

        url = 'https://xinghuo.xfyun.cn/iflygpt/u/prompt/getPromptList'

        return await self.__request(url, self.__request_headers, Method.GET)

    async def get_chat_history(self, chat_id: int) -> dict:
        """
        获取会话记录
        :param chat_id：会话 ID
        :return：会话记录
        """

        url = f'https://xinghuo.xfyun.cn/iflygpt/u/chat_history/{chat_id}'

        return await self.__request(url, self.__request_headers, Method.GET)

    async def create_chat_list(self) -> dict:
        """
        创建新的会话
        :return：创建的会话
        """

        url = 'https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/create-chat-list'
        headers = self.__request_headers.copy()
        headers['Content-Type'] = 'application/json;charset=UTF-8'

        return await self.__request(url, headers, Method.POST)

    async def rename_chat(self, chat_id: int, name: str) -> bool:
        """
        重命名会话
        :param chat_id：会话 ID
        :param name：新的会话名
        :return：是否成功
        """

        url = 'https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/rename-chat-list'
        headers = self.__request_headers.copy()
        headers['Content-Type'] = 'application/json;charset=UTF-8'

        _json = {'chatListId': chat_id, 'chatListName': name}

        return await self.__request(url, headers, Method.POST, json=_json)

    async def delete_chat(self, chat_id: int) -> bool:
        """
        删除会话
        :param chat_id：会话 ID
        :return：是否成功
        """

        url = 'https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/del-chat-list'
        headers = self.__request_headers.copy()
        headers['Content-Type'] = 'application/json;charset=UTF-8'
        _json = {'chatListId': chat_id}

        return await self.__request(url, headers, Method.POST, json=_json)

    async def chat(
            self,
            chat_id: int,
            text: str,
            gt_token: str,
            fd: str = '',
            is_bot: int = 0,
            client_type: int = 1
    ) -> str:
        """
        在某个会话中聊天
        :param chat_id：会话 ID
        :param text：发送的文本
        :param gt_token：反爬校验 token，半小时有效(固定一个值即可，有幂等性)
        :param fd：可选参数，目前没发现有什么用>_<
        :param is_bot：可选参数，目前没发现有什么用>_<
        :param client_type：固定是 1 即可
        :return：AI 响应报文
        """

        url = 'https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/chat'
        headers = self.__request_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        data = {
            'fd': fd,
            'isBot': is_bot,
            'chatId': chat_id,
            'text': text,
            'GtToken': gt_token,
            'clientType': client_type
        }

        return await self.__stream(url, headers, self.__cookies, data)

    async def re_answer(
            self,
            chat_id: int,
            text: str,
            gt_token: str,
            fd: str = '',
            sid: str = '',
            is_bot: int = 0,
            client_type: int = 1
    ) -> str:
        """
        重新回答
        :param chat_id：会话 ID
        :param text：发送的文本
        :param gt_token：反爬校验 token，半小时有效(固定一个值即可，有幂等性)
        :param fd：可选参数，目前没发现有什么用>_<
        :param sid：可选参数，目前没发现有什么用>_<
        :param is_bot：可选参数，目前没发现有什么用>_<
        :param client_type：固定是 1 即可
        :return：AI 响应报文
        """

        url = 'https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/reAnswer'
        headers = self.__request_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        data = {
            'fd': fd,
            'isBot': is_bot,
            'chatId': chat_id,
            'sid': sid,
            'text': text,
            'GtToken': gt_token,
            'clientType': client_type
        }

        return await self.__stream(url, headers, self.__cookies, data)

    async def __request(
            self,
            url: str,
            headers: dict,
            method: Method,
            params: Optional[dict] = {},
            json: Optional[dict] = {},
            data: Optional[dict] = {}
    ) -> Union[List[dict], dict, bool]:
        match method:
            case Method.GET:
                resp = await self.__session.get(
                    url,
                    headers=headers,
                    cookies=self.__cookies,
                    params=params
                )
            case Method.POST:
                resp = await self.__session.post(
                    url,
                    headers=headers,
                    cookies=self.__cookies,
                    json=json,
                    data=data
                )
            case _:
                raise IflyGPTError(f'Unsupported method: {method}')
        if resp.status_code == 200:
            resp_json = resp.json()
            if resp_json['code'] == 0:
                return resp_json['data']
            else:
                raise RequestError(resp_json['desc'])

        elif resp.status_code == 401:
            # TODO 401 logic optimization
            raise AuthError(resp.text)
        else:
            raise APIConnectionError(resp.text)

    async def __stream(
            self,
            url,
            headers,
            cookies,
            data
    ) -> str:
        async with self.__session.stream(
                Method.POST.value,
                url,
                headers=headers,
                cookies=cookies,
                data=data
        ) as resp:
            if resp.status_code == 200:
                encoded_data = ''
                resp_text = ''
                try:
                    prefix_len = len('data:')
                    async for line in resp.aiter_lines():
                        if line:
                            encoded_line = line[prefix_len:]
                            if encoded_line == '<end>':
                                resp_text += decode(encoded_data, True)
                                break
                            encoded_data += encoded_line
                            if encoded_line.endswith('='):
                                resp_text += decode(encoded_data, True)
                                encoded_data = ''
                    return resp_text
                except IflyGPTError as exp:
                    raise exp
            elif resp.status_code == 401:
                # TODO 401 logic optimization
                raise AuthError(resp.text)
            else:
                raise APIConnectionError(resp.text)
