import requests
import json

BASE_URL = 'http://localhost:8000/api'

def login(username, password):
    response = requests.post(
        f'{BASE_URL}/login/',
        json={'username': username, 'password': password}
    )
    print(f'登录 {username}: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token') or data.get('token') or data.get('access')
        if token:
            print(f'  Token: {str(token)[:50]}...')
        return token
    else:
        print(f'  错误: {response.text}')
        return None

def test_inspector_pending(token):
    print('\n=== 测试质检员待办列表 ===')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/inspector/pending/', headers=headers)
    print(f'状态码: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        print(f'待办工单分组数: {len(data)}')
        for group in data:
            if isinstance(group, dict):
                print(f'\n  工单: {group.get("work_order_no")} ({group.get("product_name")})')
                reports = group.get('reports', [])
                for report in reports:
                    print(f'    - {report.get("worker_name")} | {report.get("process_name")} | {report.get("quantity")}件 | ID={report.get("id")}')
    else:
        print(f'错误: {response.text}')

def test_quality_inspection(token, report_id, passed, rework, scrapped):
    print(f'\n=== 测试质检审核 (报工ID={report_id}) ===')
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'passed_quantity': passed,
        'rework_quantity': rework,
        'scrapped_quantity': scrapped
    }
    response = requests.post(
        f'{BASE_URL}/workreports/{report_id}/inspect/',
        json=data,
        headers=headers
    )
    print(f'状态码: {response.status_code}')
    print(f'请求数据: {data}')
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, dict) and 'data' in result:
            result = result['data']
        print(f'成功: status={result.get("status")}, passed={result.get("passed_quantity")}, rework={result.get("rework_quantity")}, scrapped={result.get("scrapped_quantity")}')
        print(f'是否锁定: {result.get("is_locked")}')
    else:
        print(f'错误: {response.text}')

def test_inspector_history(token):
    print('\n=== 测试质检历史列表 ===')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/inspector/history/', headers=headers)
    print(f'状态码: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        print(f'历史记录数: {len(data)}')
        for item in data[:5]:
            if isinstance(item, dict):
                print(f'  - {item.get("worker_name")} | {item.get("process_name")} | {item.get("status_name")} | 合格={item.get("passed_quantity")}')
    else:
        print(f'错误: {response.text}')

def test_worker_rework_tasks(token):
    print('\n=== 测试工人返修任务列表 ===')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/worker/rework-tasks/', headers=headers)
    print(f'状态码: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        print(f'返修任务数: {len(data)}')
        for task in data:
            if isinstance(task, dict):
                print(f'  - ID={task.get("id")} | {task.get("process_name")} | 数量={task.get("quantity")} | 状态={task.get("status_name")}')
    else:
        print(f'错误: {response.text}')

def get_first_pending_report(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/inspector/pending/', headers=headers)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        for group in data:
            reports = group.get('reports', [])
            for report in reports:
                if report.get('status') == 'pending':
                    return report
    return None

def test_quantity_validation(token, report_id, report_qty):
    print('\n=== 测试数量校验逻辑 ===')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试：数量不匹配
    print(f'测试1: 数量不匹配 (合格{report_qty-2}+返工0+报废0={report_qty-2} ≠ 报工{report_qty})')
    data = {'passed_quantity': report_qty-2, 'rework_quantity': 0, 'scrapped_quantity': 0}
    response = requests.post(
        f'{BASE_URL}/workreports/{report_id}/inspect/',
        json=data,
        headers=headers
    )
    print(f'  状态码: {response.status_code}')
    if response.status_code == 400:
        result = response.json()
        print(f'  ✓ 正确拦截: {result.get("message")}')
    else:
        print(f'  ✗ 错误: 应该返回400')
    
    # 测试：数量匹配（有返工和报废）
    passed = report_qty - 5
    rework = 3
    scrapped = 2
    print(f'\n测试2: 数量匹配 (合格{passed}+返工{rework}+报废{scrapped}={report_qty} = 报工{report_qty})')
    data = {'passed_quantity': passed, 'rework_quantity': rework, 'scrapped_quantity': scrapped}
    response = requests.post(
        f'{BASE_URL}/workreports/{report_id}/inspect/',
        json=data,
        headers=headers
    )
    print(f'  状态码: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, dict) and 'data' in result:
            result = result['data']
        print(f'  ✓ 审核通过')
        print(f'    status={result.get("status")}')
        print(f'    is_locked={result.get("is_locked")}')
        print(f'    passed={result.get("passed_quantity")}')
        print(f'    rework={result.get("rework_quantity")}')
        print(f'    scrapped={result.get("scrapped_quantity")}')
        return True
    else:
        print(f'  ✗ 错误: {response.text}')
        return False

def test_lock_mechanism(worker_token, report_id):
    print('\n=== 测试数据锁定机制 ===')
    headers = {'Authorization': f'Bearer {worker_token}'}
    
    print('测试: 工人尝试修改已锁定的报工记录')
    data = {'quantity': 100}
    response = requests.put(
        f'{BASE_URL}/workreports/{report_id}/',
        json=data,
        headers=headers
    )
    print(f'  状态码: {response.status_code}')
    if response.status_code == 400 or response.status_code == 403:
        result = response.json()
        print(f'  ✓ 正确拦截: {result.get("message")}')
    else:
        print(f'  响应: {response.text[:200]}')
    
    print('\n测试: 工人尝试删除已锁定的报工记录')
    response = requests.delete(
        f'{BASE_URL}/workreports/{report_id}/',
        headers=headers
    )
    print(f'  状态码: {response.status_code}')
    if response.status_code == 400 or response.status_code == 403:
        result = response.json()
        print(f'  ✓ 正确拦截: {result.get("message")}')
    else:
        print(f'  响应: {response.text[:200]}')

def test_salary_calculation(inspector_token):
    print('\n=== 测试工资计算逻辑 ===')
    headers = {'Authorization': f'Bearer {inspector_token}'}
    response = requests.get(f'{BASE_URL}/workreports/', headers=headers)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        for report in data:
            if report.get('status') == 'passed' and report.get('passed_quantity', 0) > 0:
                print(f'  报工ID: {report.get("id")}')
                print(f'  工序: {report.get("process_name")}')
                print(f'  报工数量: {report.get("quantity")}')
                print(f'  合格数量: {report.get("passed_quantity")}')
                print(f'  工序单价: {report.get("process_price")}')
                print(f'  工资金额: {report.get("salary_amount")}')
                expected = report.get('passed_quantity', 0) * (report.get('process_price') or 0)
                print(f'  预期金额: {expected}')
                if abs((report.get('salary_amount') or 0) - expected) < 0.01:
                    print(f'  ✓ 工资计算正确')
                else:
                    print(f'  ✗ 工资计算错误')
                return True
        print(f'  暂无可计算工资的记录')
    return False

if __name__ == '__main__':
    print('=' * 60)
    print('质检审核模块 API 测试')
    print('=' * 60)

    inspector_token = login('inspector01', '123456')
    
    if inspector_token:
        # 1. 测试待办列表
        test_inspector_pending(inspector_token)
        
        # 2. 获取一个待质检的报工记录
        pending_report = get_first_pending_report(inspector_token)
        if pending_report:
            report_id = pending_report['id']
            report_qty = pending_report['quantity']
            report_worker_name = pending_report.get('worker_name')
            print(f'\n找到待质检记录: ID={report_id}, 数量={report_qty}, 工人={report_worker_name}')
            
            # 3. 测试数量校验和质检审核（有返工的情况）
            inspect_success = test_quantity_validation(inspector_token, report_id, report_qty)
            
            if inspect_success:
                # 4. 测试数据锁定机制（用正确的工人账号）
                worker_username_map = {
                    '张三': 'zhangsan',
                    '李四': 'lisi',
                    '王五': 'wangwu',
                    '赵六': 'zhaoliu'
                }
                worker_username = worker_username_map.get(report_worker_name, 'zhangsan')
                correct_worker_token = login(worker_username, '123456')
                if correct_worker_token:
                    test_lock_mechanism(correct_worker_token, report_id)
                    test_worker_rework_tasks(correct_worker_token)
            
            # 5. 获取另一个待质检记录，测试完全通过的情况
            pending_report2 = get_first_pending_report(inspector_token)
            if pending_report2:
                report_id2 = pending_report2['id']
                report_qty2 = pending_report2['quantity']
                report_worker_name2 = pending_report2.get('worker_name')
                print(f'\n找到另一个待质检记录: ID={report_id2}, 数量={report_qty2}, 工人={report_worker_name2}')
                test_quality_inspection(inspector_token, report_id2, report_qty2, 0, 0)
                
                # 6. 测试工资计算
                test_salary_calculation(inspector_token)
        
        # 7. 测试历史记录
        test_inspector_history(inspector_token)

    print('\n' + '=' * 60)
    print('测试完成')
    print('=' * 60)
