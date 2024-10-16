# author: zuohuaiyu
# date: 2024/10/11 13:42
import requests


# from tabulate import tabulate

class LrcClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def get_data(self, page=1, per_page=10):
        try:
            response = requests.get(
                f'{self.base_url}/data',
                params={'page': page, 'per_page': per_page}
            )
            response.raise_for_status()  # 如果响应状态码不是200，抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def get_columns(self):
        try:
            response = requests.get(f'{self.base_url}/columns')
            response.raise_for_status()
            return response.json()['columns']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching columns: {e}")
            return None

    def update_json(self, data):
        """
        向服务器发送POST请求以更新JSON数据

        :param data: 要发送的JSON数据
        :return: 是否更新成功
        """
        url = f"{self.base_url}/api/json"

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # 如果响应状态码不是200，将引发异常
            return True
        except requests.RequestException as e:
            print(f"更新JSON数据时发生错误: {str(e)}")
            return False

    def download_json(self):
        """
        从服务器下载JSON数据
        :return: 包含JSON数据的字典，或者在发生异常时返回None
        """
        url = f"{self.base_url}/api/json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error fetching json: {e}")
            return None

    def display_data(self, data):
        if not data or 'data' not in data:
            print("No data to display")
            return

        # 提取分页信息
        pagination = data['pagination']
        records = data['data']

        # # 如果没有记录，直接返回
        # if not records:
        #     print("No records found")
        #     return
        #
        # # 使用tabulate创建表格
        # headers = records[0].keys()
        # table = [[row[col] for col in headers] for row in records]
        # print(tabulate(table, headers=headers, tablefmt="grid"))
        #
        # # 打印分页信息
        # print(f"\nPage {pagination['current_page']} of {pagination['total_pages']}")
        # print(f"Showing {len(records)} of {pagination['total_records']} records")
