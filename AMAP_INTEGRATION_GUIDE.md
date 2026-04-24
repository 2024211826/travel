# 高德地图地理编码服务集成指南

## 📋 概述

本模块为旅游地点推荐系统提供高德地图地理编码/逆地理编码服务集成，支持：

- **地理编码**：将地址转换为经纬度坐标
- **逆地理编码**：将经纬度坐标转换为详细地址
- **IP 定位**：根据 IP 地址获取大致位置
- **批量处理**：批量查询多个地点坐标
- **距离计算**：计算两点间的球面距离

## 🔧 安装依赖

```bash
pip install requests
```

## 🚀 快速开始

### 1. 获取 API Key

1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册/登录账号
3. 进入"控制台" → "应用管理" → "我的应用"
4. 点击"创建新应用"
5. 添加 Key，选择"Web 服务"类型
6. 记录 API Key 和安全密钥（推荐使用安全密钥）

### 2. 基本使用

```python
from amap_geo_service import AMapGeoService

# 初始化服务
geo_service = AMapGeoService(
    api_key="您的 API Key",
    security_code="您的安全密钥"  # 可选但推荐
)

# 地理编码：地址 → 坐标
result = geo_service.geocode("北京大学", "北京市")
print(f"坐标：{result['location']}")
# 输出：{'lng': 116.305, 'lat': 39.987}

# 逆地理编码：坐标 → 地址
result = geo_service.regeocode(116.305, 39.987)
print(f"地址：{result['formatted_address']}")
# 输出："北京市海淀区中关村大街 1 号"

# IP 定位
result = geo_service.get_ip_location()
print(f"当前位置：{result['province']} {result['city']}")
```

## 📖 API 详细说明

### AMapGeoService 类

#### 初始化参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `api_key` | str | 是 | 高德地图 Web 服务 API Key |
| `security_code` | str | 否 | 安全密钥（用于签名验证） |

#### 方法列表

##### 1. `geocode(address, city=None)`

地理编码 - 将地址转换为经纬度

**参数：**
- `address` (str): 地址字符串
- `city` (str, optional): 城市名称，提高精度

**返回值：**
```python
{
    'location': {'lng': 116.305, 'lat': 39.987},
    'formatted_address': '北京市海淀区中关村大街 1 号',
    'country': '中国',
    'province': '北京市',
    'city': '北京市',
    'district': '海淀区',
    'street': '中关村大街',
    'number': '1 号',
    'confidence': '10',
    'level': '门牌号'
}
```

**示例：**
```python
# 查询景点坐标
result = geo_service.geocode("故宫博物院", "北京市")
if result.get('location'):
    lng = result['location']['lng']
    lat = result['location']['lat']
    print(f"故宫坐标：{lng}, {lat}")
```

---

##### 2. `regeocode(longitude, latitude, extensions='base')`

逆地理编码 - 将经纬度转换为地址

**参数：**
- `longitude` (float): 经度
- `latitude` (float): 纬度
- `extensions` (str): 返回信息控制，'base' 或 'all'

**返回值：**
```python
{
    'formatted_address': '北京市海淀区中关村大街 1 号',
    'address_component': {
        'province': '北京市',
        'city': '北京市',
        'district': '海淀区',
        'township': '中关村街道',
        'street_number': '中关村大街 1 号'
    },
    'location': {'lng': 116.305, 'lat': 39.987},
    'pois': [...]  # 当 extensions='all' 时包含周边 POI
}
```

**示例：**
```python
# 获取用户当前位置的详细信息
result = geo_service.regeocode(116.305, 39.987, extensions='all')
print(f"当前地址：{result['formatted_address']}")

# 获取周边设施
if 'pois' in result:
    for poi in result['pois'][:5]:
        print(f"附近：{poi['name']} - {poi['type']}")
```

---

##### 3. `get_ip_location(ip=None)`

IP 定位 - 根据 IP 地址获取位置

**参数：**
- `ip` (str, optional): IP 地址，不传则使用请求 IP

**返回值：**
```python
{
    'province': '北京市',
    'city': '北京市',
    'adcode': '110000',
    'rectangle': '116.011934,39.661271;116.782983,40.216496',
    'isp': '中国联通',
    'location_type': 'IP 定位'
}
```

**示例：**
```python
# 获取当前用户大致位置
result = geo_service.get_ip_location()
print(f"用户在：{result['province']} {result['city']}")

# 查询特定 IP
result = geo_service.get_ip_location("8.8.8.8")
```

---

##### 4. `batch_geocode(addresses, city=None)`

批量地理编码

**参数：**
- `addresses` (List[str]): 地址列表（最多 10 个）
- `city` (str, optional): 城市名称

**返回值：** 地理编码结果列表

**示例：**
```python
# 批量查询多个景点坐标
scenic_spots = ["故宫", "颐和园", "天坛", "长城"]
results = geo_service.batch_geocode(scenic_spots, "北京市")

for result in results:
    if result.get('location'):
        print(f"{result['query_address']}: {result['location']}")
    else:
        print(f"{result['query_address']}: 未找到")
```

---

##### 5. `calculate_distance(origin, destination)`

计算两点间距离（Haversine 公式）

**参数：**
- `origin` (tuple): 起点 (经度，纬度)
- `destination` (tuple): 终点 (经度，纬度)

**返回值：**
```python
{
    'distance_km': 5.67,
    'distance_m': 5670.0,
    'origin': {'lng': 116.305, 'lat': 39.987},
    'destination': {'lng': 116.405, 'lat': 39.907}
}
```

**示例：**
```python
# 计算当前位置到景点的距离
current_pos = (116.305, 39.987)
spot_pos = (116.405, 39.907)
distance = geo_service.calculate_distance(current_pos, spot_pos)
print(f"距离：{distance['distance_km']:.2f} 公里")
```

## 🎯 在旅游系统中的应用场景

### 场景 1: 用户输入景点名称 → 获取坐标

```python
def search_scenic_spot(name, city=None):
    """搜索景点并返回坐标"""
    result = geo_service.geocode(name, city)
    if result.get('location'):
        return {
            'name': name,
            'location': result['location'],
            'address': result['formatted_address'],
            'district': result.get('district', '')
        }
    return None

# 使用
spot = search_scenic_spot("颐和园", "北京市")
```

### 场景 2: 获取用户当前位置

```python
def get_user_location(gps_coords=None):
    """获取用户当前位置信息"""
    if gps_coords:
        # 使用 GPS 坐标进行逆地理编码
        result = geo_service.regeocode(gps_coords[0], gps_coords[1])
        return {
            'type': 'GPS',
            'address': result['formatted_address'],
            'district': result['address_component']['district']
        }
    else:
        # 使用 IP 定位
        result = geo_service.get_ip_location()
        return {
            'type': 'IP',
            'province': result['province'],
            'city': result['city']
        }

# 使用
location = get_user_location()  # IP 定位
location = get_user_location((116.305, 39.987))  # GPS 定位
```

### 场景 3: 查找附近设施

```python
def find_nearby_facilities(longitude, latitude, facility_type=None, radius=1000):
    """查找指定位置附近的设施"""
    result = geo_service.regeocode(longitude, latitude, extensions='all')
    
    facilities = []
    if 'pois' in result:
        for poi in result['pois']:
            if facility_type is None or facility_type in poi.get('type', ''):
                facilities.append({
                    'name': poi['name'],
                    'type': poi.get('type', ''),
                    'distance': poi.get('distance', ''),
                    'address': poi.get('address', '')
                })
    
    # 按距离排序
    facilities.sort(key=lambda x: float(x['distance']) if x['distance'] else 9999)
    return facilities[:10]  # 返回最近的 10 个

# 使用
nearby = find_nearby_facilities(116.305, 39.987, facility_type="餐饮服务")
```

### 场景 4: 路径规划前的距离计算

```python
def calculate_route_distances(current_pos, destinations):
    """计算当前位置到多个目的地的距离"""
    distances = []
    for dest in destinations:
        if dest.get('location'):
            dist = geo_service.calculate_distance(
                (current_pos['lng'], current_pos['lat']),
                (dest['location']['lng'], dest['location']['lat'])
            )
            distances.append({
                'name': dest['name'],
                'distance_km': dist['distance_km'],
                'location': dest['location']
            })
    
    # 按距离排序
    distances.sort(key=lambda x: x['distance_km'])
    return distances

# 使用
current = {'lng': 116.305, 'lat': 39.987}
spots = [
    {'name': '故宫', 'location': {'lng': 116.397, 'lat': 39.916}},
    {'name': '天坛', 'location': {'lng': 116.407, 'lat': 39.882}}
]
sorted_spots = calculate_route_distances(current, spots)
```

## ⚠️ 注意事项

1. **API Key 安全**
   - 不要将 API Key 提交到代码仓库
   - 使用环境变量或配置文件存储
   - 建议启用安全密钥签名

2. **配额限制**
   - 个人认证：QPS 限制 50，日配额 50000
   - 企业认证：更高配额
   - 查看配额：https://lbs.amap.com/api/quota

3. **错误处理**
   ```python
   try:
       result = geo_service.geocode("无效地址")
   except Exception as e:
       print(f"查询失败：{e}")
   ```

4. **性能优化**
   - 批量查询时使用 `batch_geocode`
   - 对频繁查询的结果进行缓存
   - 避免在短时间内大量并发请求

## 📝 配置示例

### 使用环境变量

```python
import os
from amap_geo_service import AMapGeoService

geo_service = AMapGeoService(
    api_key=os.getenv('AMAP_API_KEY'),
    security_code=os.getenv('AMAP_SECURITY_CODE')
)
```

### 使用配置文件

```python
# config.py
AMAP_CONFIG = {
    'api_key': 'your_api_key',
    'security_code': 'your_security_code'
}

# main.py
from config import AMAP_CONFIG
from amap_geo_service import AMapGeoService

geo_service = AMapGeoService(**AMAP_CONFIG)
```

## 🔗 相关文档

- [高德地图 Web 服务 API](https://lbs.amap.com/api/webservice/guide)
- [地理编码 API](https://lbs.amap.com/api/webservice/guide/api/georegeo)
- [IP 定位 API](https://lbs.amap.com/api/webservice/guide/api/ipconfig)
- [距离测量 API](https://lbs.amap.com/api/webservice/guide/api/distance)

## 📞 技术支持

如有问题，请查阅：
- 高德开放平台官方文档
- API 错误码说明：https://lbs.amap.com/api/webservice/guide/tools/info
