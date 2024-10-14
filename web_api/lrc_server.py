# author: zuohuaiyu
# date: 2024/10/11 13:29
from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)  # 启用CORS，允许跨域请求

JSON_FILE_PATH = 'config.json'


# 加载CSV文件
def load_csv():
    try:
        # 假设CSV文件名为data.csv，在同一目录下
        df = pd.read_csv('../db/lrc_alarm.csv')
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None


@app.route('/data', methods=['GET'])
def get_data():
    # 获取查询参数
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # 加载数据
    df = load_csv()
    df = df.sort_index(ascending=False)
    if df is None:
        return jsonify({
            'error': 'Failed to load data'
        }), 500

    # 计算总页数和记录数
    total_records = len(df)
    total_pages = (total_records + per_page - 1) // per_page

    # 验证页码
    if page < 1 or page > total_pages:
        return jsonify({
            'error': 'Invalid page number'
        }), 400

    # 计算切片索引
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_records)

    # 获取当前页的数据
    page_data = df.iloc[start_idx:end_idx].to_dict('records')

    # 返回结果
    return jsonify({
        'data': page_data,
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_records': total_records
        }
    })


@app.route('/columns', methods=['GET'])
def get_columns():
    df = load_csv()
    if df is None:
        return jsonify({
            'error': 'Failed to load data'
        }), 500

    return jsonify({
        'columns': list(df.columns)
    })


def read_json_file():
    if not os.path.exists(JSON_FILE_PATH):
        return {}
    with open(JSON_FILE_PATH, 'r') as file:
        return json.load(file)


def write_json_file(data):
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)


@app.route('/api/json', methods=['GET'])
def get_json():
    data = read_json_file()
    return jsonify(data)


@app.route('/api/json', methods=['POST'])
def update_json():
    data = request.json
    write_json_file(data)
    return jsonify({"status": "success"})


if __name__ == '__main__':
    app.run(debug=True)
