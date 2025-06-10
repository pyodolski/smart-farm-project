import API_BASE_URL from './config';

export const farmService = {
  async getFarmDetail(farmId) {
    const response = await fetch(`${API_BASE_URL}/api/farms/${farmId}`, {
      credentials: 'include'
    });
    if (!response.ok) throw new Error('농장 정보를 불러오는데 실패했습니다.');
    return response.json();
  },

  async getWeather(location) {
    const response = await fetch(`${API_BASE_URL}/api/weather?city=${encodeURIComponent(location)}`, {
      credentials: 'include'
    });
    if (!response.ok) throw new Error('날씨 정보를 불러오는데 실패했습니다.');
    return response.json();
  }
};

export const greenhouseService = {
  async getGreenhouseList(farmId) {
    const response = await fetch(`${API_BASE_URL}/api/greenhouses/list/${farmId}`, {
      credentials: 'include'
    });
    if (!response.ok) throw new Error('온실 목록을 불러오는데 실패했습니다.');
    return response.json();
  },

  async getGridData(greenhouseId) {
    const response = await fetch(`${API_BASE_URL}/api/greenhouses/api/grid?id=${greenhouseId}`, {
      credentials: 'include'
    });
    if (!response.ok) throw new Error('그리드 데이터를 불러오는데 실패했습니다.');
    return response.json();
  },

  async updateGrid(greenhouseId, data) {
    const response = await fetch(`${API_BASE_URL}/api/greenhouses/update/${greenhouseId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('그리드 업데이트에 실패했습니다.');
    return response.json();
  },

  async createGreenhouse(data) {
    const response = await fetch(`${API_BASE_URL}/api/greenhouses/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('하우스 생성에 실패했습니다.');
    return response.json();
  },

  async deleteGreenhouse(greenhouseId) {
    const response = await fetch(`${API_BASE_URL}/api/greenhouses/${greenhouseId}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    if (!response.ok) throw new Error('하우스 삭제에 실패했습니다.');
    return response.json();
  }
}; 