"""
高德地图地理编码/逆地理编码服务集成模块

用于旅游地点推荐系统中的位置服务：
- 将地址转换为经纬度（地理编码）
- 将经纬度转换为地址（逆地理编码）
- 获取当前位置信息
- 支持景点、学校、设施等地点的坐标查询
"""

import requests
import hashlib
import time
from typing import Optional, Dict, List, Any


class AMapGeoService:
    """高德地图地理编码服务类"""
    
    def __init__(self, api_key: str, security_code: Optional[str] = None):
        """
        初始化高德地图服务
        
        Args:
            api_key: 高德地图 Web 服务 API Key
            security_code: 高德地图安全密钥（用于签名验证，可选但推荐）
        """
        self.api_key = api_key
        self.security_code = security_code
        self.geocode_url = "https://restapi.amap.com/v3/geocode/geo"
        self.regeocode_url = "https://restapi.amap.com/v3/geocode/regeo"
        self.ip_location_url = "https://restapi.amap.com/v3/ip"
        
    def _generate_signature(self, params: Dict[str, str]) -> str:
        """
        生成请求签名（如果使用安全密钥）
        
        Args:
            params: 请求参数字典
            
        Returns:
            签名字符串
        """
        if not self.security_code:
            return ""
        
        # 按参数名排序
        sorted_params = sorted(params.items())
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 添加安全密钥
        string_to_sign = f"{param_string}&{self.security_code}"
        
        # MD5 签名
        signature = hashlib.md5(string_to_sign.encode('utf-8')).hexdigest()
        return signature
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送 HTTP 请求
        
        Args:
            url: 请求 URL
            params: 请求参数
            
        Returns:
            API 响应数据
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        # 添加基础参数
        params['key'] = self.api_key
        params['output'] = 'json'
        
        # 如果需要签名，添加签名和时间戳
        if self.security_code:
            params['timestamp'] = str(int(time.time()))
            params['sig'] = self._generate_signature(params)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == '0':
                raise Exception(f"API 错误: {result.get('info', '未知错误')}")
            
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
    
    def geocode(self, address: str, city: Optional[str] = None) -> Dict[str, Any]:
        """
        地理编码：将地址转换为经纬度
        
        Args:
            address: 地址字符串（如："北京市海淀区中关村大街1号"）
            city: 城市名称（可选，提高精度）
            
        Returns:
            包含经纬度的字典：
            {
                'location': {'lng': 经度, 'lat': 纬度},
                'formatted_address': 标准化地址,
                'country', 'province', 'city', 'district' 等
            }
            
        Example:
            >>> geo = AMapGeoService(api_key="your_key")
            >>> result = geo.geocode("北京大学", "北京市")
            >>> print(result['location'])
            {'lng': 116.305, 'lat': 39.987}
        """
        params = {
            'address': address,
        }
        
        if city:
            params['city'] = city
            
        result = self._make_request(self.geocode_url, params)
        
        if result.get('geocodes') and len(result['geocodes']) > 0:
            geocode = result['geocodes'][0]
            location_str = geocode.get('location', '')
            
            if location_str:
                lng, lat = map(float, location_str.split(','))
                return {
                    'location': {'lng': lng, 'lat': lat},
                    'formatted_address': geocode.get('formatted_address', ''),
                    'country': geocode.get('country', ''),
                    'province': geocode.get('province', ''),
                    'city': geocode.get('city', ''),
                    'district': geocode.get('district', ''),
                    'street': geocode.get('street', ''),
                    'number': geocode.get('number', ''),
                    'confidence': geocode.get('confidence', ''),
                    'level': geocode.get('level', '')
                }
        
        return {'location': None, 'error': '未找到匹配的地址'}
    
    def regeocode(self, longitude: float, latitude: float, 
                  extensions: str = 'base') -> Dict[str, Any]:
        """
        逆地理编码：将经纬度转换为地址
        
        Args:
            longitude: 经度
            latitude: 纬度
            extensions: 返回信息控制 ('base' 或 'all')
            
        Returns:
            包含地址信息的字典：
            {
                'formatted_address': 格式化地址,
                'address_component': {省、市、区等信息},
                'pois': 附近兴趣点列表（当 extensions='all' 时）
            }
            
        Example:
            >>> geo = AMapGeoService(api_key="your_key")
            >>> result = geo.regeocode(116.305, 39.987)
            >>> print(result['formatted_address'])
            "北京市海淀区中关村大街1号"
        """
        params = {
            'location': f'{longitude},{latitude}',
            'extensions': extensions,
        }
        
        result = self._make_request(self.regeocode_url, params)
        
        if result.get('regeocode'):
            regeocode = result['regeocode']
            address_component = regeocode.get('addressComponent', {})
            
            response_data = {
                'formatted_address': regeocode.get('formatted_address', ''),
                'address_component': {
                    'province': address_component.get('province', ''),
                    'city': address_component.get('city', ''),
                    'citycode': address_component.get('citycode', ''),
                    'district': address_component.get('district', ''),
                    'township': address_component.get('township', ''),
                    'neighborhood': address_component.get('neighborhood', {}).get('name', ''),
                    'building': address_component.get('building', {}).get('name', ''),
                    'street_number': address_component.get('streetNumber', {}).get('street', '') + 
                                   address_component.get('streetNumber', {}).get('number', '')
                },
                'location': {'lng': longitude, 'lat': latitude}
            }
            
            # 如果请求详细信息，添加周边 POI
            if extensions == 'all':
                response_data['pois'] = regeocode.get('pois', [])
            
            return response_data
        
        return {'formatted_address': '', 'error': '未找到地址信息'}
    
    def get_ip_location(self, ip: Optional[str] = None) -> Dict[str, Any]:
        """
        IP 定位：根据 IP 地址获取位置信息
        
        Args:
            ip: IP 地址（可选，不传则使用请求 IP）
            
        Returns:
            包含位置信息的字典：
            {
                'province': 省份,
                'city': 城市,
                'adcode': 行政区划代码,
                'rectangle': 矩形范围
            }
            
        Example:
            >>> geo = AMapGeoService(api_key="your_key")
            >>> result = geo.get_ip_location()
            >>> print(f"当前位置：{result['province']} {result['city']}")
        """
        params = {}
        
        if ip:
            params['ip'] = ip
            
        result = self._make_request(self.ip_location_url, params)
        
        return {
            'province': result.get('province', ''),
            'city': result.get('city', ''),
            'adcode': result.get('adcode', ''),
            'rectangle': result.get('rectangle', ''),
            'isp': result.get('isp', ''),
            'location_type': 'IP 定位'
        }
    
    def batch_geocode(self, addresses: List[str], city: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        批量地理编码（最多 10 个地址）
        
        Args:
            addresses: 地址列表
            city: 城市名称
            
        Returns:
            地理编码结果列表
        """
        results = []
        for address in addresses:
            try:
                result = self.geocode(address, city)
                result['query_address'] = address
                results.append(result)
            except Exception as e:
                results.append({
                    'query_address': address,
                    'error': str(e),
                    'location': None
                })
        return results
    
    def calculate_distance(self, origin: tuple, destination: tuple) -> Dict[str, Any]:
        """
        计算两点间的距离（使用高德地图距离测量 API）
        
        Args:
            origin: 起点 (经度，纬度)
            destination: 终点 (经度，纬度)
            
        Returns:
            包含距离信息的字典
        """
        # 注意：这需要额外的 distance API，这里提供简化版本
        # 实际项目中需要调用 https://restapi.amap.com/v3/distance
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1 = origin
        lon2, lat2 = destination
        
        # Haversine 公式计算球面距离
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # 地球平均半径（公里）
        
        return {
            'distance_km': c * r,
            'distance_m': c * r * 1000,
            'origin': {'lng': lon1, 'lat': lat1},
            'destination': {'lng': lon2, 'lat': lat2}
        }


# 使用示例和测试函数
def demo_usage():
    """演示如何使用地理编码服务"""
    
    # 注意：请替换为您的真实 API Key
    API_KEY = "您的高德地图 API Key"
    SECURITY_CODE = "您的安全密钥"  # 可选
    
    # 初始化服务
    geo_service = AMapGeoService(api_key=API_KEY, security_code=SECURITY_CODE)
    
    print("=" * 60)
    print("高德地图地理编码服务演示")
    print("=" * 60)
    
    # 示例 1: 地理编码 - 查询景点坐标
    print("\n1. 地理编码示例 - 查询'北京大学'的坐标:")
    try:
        result = geo_service.geocode("北京大学", "北京市")
        if result.get('location'):
            print(f"   地址：{result['formatted_address']}")
            print(f"   坐标：经度 {result['location']['lng']}, 纬度 {result['location']['lat']}")
            print(f"   区域：{result['city']} {result['district']}")
    except Exception as e:
        print(f"   错误：{e}")
    
    # 示例 2: 逆地理编码 - 根据坐标获取地址
    print("\n2. 逆地理编码示例 - 查询坐标 (116.305, 39.987) 的地址:")
    try:
        result = geo_service.regeocode(116.305, 39.987)
        if result.get('formatted_address'):
            print(f"   地址：{result['formatted_address']}")
            print(f"   省份：{result['address_component']['province']}")
            print(f"   城市：{result['address_component']['city']}")
            print(f"   区县：{result['address_component']['district']}")
    except Exception as e:
        print(f"   错误：{e}")
    
    # 示例 3: IP 定位 - 获取当前位置
    print("\n3. IP 定位示例 - 获取当前大致位置:")
    try:
        result = geo_service.get_ip_location()
        print(f"   位置：{result['province']} {result['city']}")
        print(f"   行政区划代码：{result['adcode']}")
    except Exception as e:
        print(f"   错误：{e}")
    
    # 示例 4: 批量地理编码
    print("\n4. 批量地理编码示例 - 查询多个景点:")
    scenic_spots = [
        "故宫博物院",
        "颐和园",
        "天坛公园",
        "八达岭长城"
    ]
    try:
        results = geo_service.batch_geocode(scenic_spots, "北京市")
        for result in results:
            if result.get('location'):
                print(f"   ✓ {result['query_address']}: "
                      f"{result['location']['lng']}, {result['location']['lat']}")
            else:
                print(f"   ✗ {result['query_address']}: 未找到")
    except Exception as e:
        print(f"   错误：{e}")
    
    # 示例 5: 在旅游系统中的应用场景
    print("\n5. 旅游系统应用场景:")
    print("   - 用户输入'我想去颐和园' → 地理编码获取坐标")
    print("   - 用户当前位置 (GPS/IP) → 逆地理编码获取地址")
    print("   - 计算当前位置到景点的距离 → 路径规划")
    print("   - 查找景点附近的设施 → 周边搜索")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # 运行演示（需要有效的 API Key）
    # demo_usage()
    print("请配置您的高德地图 API Key 后运行 demo_usage() 函数")
    print("\n获取 API Key 步骤:")
    print("1. 访问 https://lbs.amap.com/")
    print("2. 注册/登录账号")
    print("3. 创建应用，选择'Web 服务'类型")
    print("4. 获取 API Key 和安全密钥")
    print("5. 替换代码中的 API_KEY 和 SECURITY_CODE")
