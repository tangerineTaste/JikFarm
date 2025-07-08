document.addEventListener('DOMContentLoaded', function() {
    const itemCountSelect = document.getElementById('item-count-select');
    const inputContainer = document.getElementById('input-container');
    const predictBtn = document.getElementById('predict-btn');
    const priceCtx = document.getElementById('price-chart').getContext('2d');
    const weatherCtx = document.getElementById('weather-chart').getContext('2d');
    let priceChart = null; // 가격 차트 인스턴스를 저장할 변수
    let weatherChart = null; // 기상 차트 인스턴스를 저장할 변수

    // 기상 데이터 캐시
    let weatherDataCache = null;
    let cachedBaseDate = null;

    const cropOptions = `
        <option value="배추">배추</option>
        <option value="무">무</option>
        <option value="고추">고추</option>
        <option value="마늘">마늘</option>
        <option value="양파">양파</option>
        <option value="사과">사과</option>
        <option value="배">배</option>
    `;

    // 오늘 날짜를 가져오는 함수
    function getTodayString() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
    }

    // 입력 필드를 생성하는 함수
    function createInputFields(count) {
        inputContainer.innerHTML = ''; // 기존 필드 초기화
        for (let i = 1; i <= count; i++) {
            const inputItem = document.createElement('div');
            inputItem.className = 'input-item';
            inputItem.style.animationDelay = `${(i - 1) * 0.1}s`;

            inputItem.innerHTML = `
                <h3>항목 ${i}</h3>
                <div class="form-group">
                    <label for="crop-select-${i}">농작물 선택</label>
                    <select id="crop-select-${i}" class="crop-select" aria-label="항목 ${i}의 농작물 종류를 선택하세요">
                        ${cropOptions}
                    </select>
                </div>
                <div class="form-group">
                    <label for="date-input-${i}">기준 날짜 선택</label>
                    <input type="date" id="date-input-${i}" class="date-input" value="${getTodayString()}" aria-label="항목 ${i}의 가격을 예측할 기준 날짜를 선택하세요">
                </div>
            `;
            inputContainer.appendChild(inputItem);
        }
    }

    // 차트를 렌더링하는 함수
    function renderCharts() {
        const count = itemCountSelect.value;
        let allValid = true;

        // 1. 유효성 검사
        for (let i = 1; i <= count; i++) {
            const dateInput = document.getElementById(`date-input-${i}`);
            if (!dateInput.value) {
                allValid = false;
                break;
            }
        }

        if (!allValid) {
            alert('모든 항목의 날짜를 선택해주세요!');
            return;
        }
        
        // 2. 데이터 준비 (가격 예측 그래프)
        const priceDatasets = [];
        const labels = [];
        const baseDateObj = new Date(document.getElementById('date-input-1').value);
        const numHistoricalDays = 7; // 과거 7일
        const numPredictedDays = 5; // 미래 5일
        const totalDays = numHistoricalDays + numPredictedDays; // 총 12일

        // 날짜 라벨 생성 (과거 7일 + 미래 5일 = 총 12일)
        for (let i = numHistoricalDays - 1; i >= 0; i--) {
            const date = new Date(baseDateObj);
            date.setDate(baseDateObj.getDate() - i);
            labels.push(`${date.getMonth() + 1}/${date.getDate()}`);
        }
        for (let i = 1; i <= numPredictedDays; i++) {
            const date = new Date(baseDateObj);
            date.setDate(baseDateObj.getDate() + i);
            labels.push(`${date.getMonth() + 1}/${date.getDate()}`);
        }

        const priceColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
        const predictedColor = '#8A2BE2'; // 예측 데이터에 사용할 다른 색상 (보라색 계열)

        for (let i = 1; i <= count; i++) {
            const cropSelect = document.getElementById(`crop-select-${i}`);
            const selectedCrop = cropSelect.value;
            
            // 과거 7일간의 임의 가격 데이터 생성
            const historicalPriceData = [];
            for (let j = 0; j < numHistoricalDays; j++) {
                historicalPriceData.push(Math.floor(Math.random() * (5000 - 1000) + 1000));
            }

            // 미래 5일간의 임의 예측 가격 데이터 생성
            const predictedPriceData = [];
            const lastHistoricalPrice = historicalPriceData[historicalPriceData.length - 1];
            for (let j = 0; j < numPredictedDays; j++) {
                // 마지막 과거 가격을 기준으로 약간의 변동을 주어 예측 가격 생성
                predictedPriceData.push(Math.floor(lastHistoricalPrice + (Math.random() * 400 - 200))); // +/- 200원 변동
            }

            // 과거 데이터와 예측 데이터를 합침
            const combinedData = historicalPriceData.concat(predictedPriceData);

            priceDatasets.push({
                label: `${selectedCrop} 가격`,
                data: combinedData,
                borderColor: priceColors[(i - 1) % priceColors.length],
                backgroundColor: priceColors[(i - 1) % priceColors.length] + '33', // 투명도 20%
                fill: false,
                tension: 0.2,
                segment: {
                    borderColor: ctx => {
                        // 예측 부분만 다른 색상 적용
                        const dataIndex = ctx.p0DataIndex; // 현재 세그먼트의 시작점 인덱스
                        if (dataIndex >= numHistoricalDays - 1) { // 마지막 과거 데이터 포인트부터 예측 시작
                            return predictedColor; 
                        }
                        return priceColors[(i - 1) % priceColors.length]; // 과거 데이터 색상
                    },
                    borderDash: ctx => {
                        // 예측 부분만 점선 적용
                        const dataIndex = ctx.p0DataIndex;
                        if (dataIndex >= numHistoricalDays - 1) {
                            return [5, 5]; // 점선
                        }
                        return []; // 실선
                    }
                }
            });
        }

        // 3. 가격 차트 생성/업데이트
        if (priceChart) {
            priceChart.destroy(); // 기존 차트가 있으면 제거
        }

        priceChart = new Chart(priceCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: priceDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: '농작물 가격 변동 그래프 (과거 7일 + 예측 5일)'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('ko-KR').format(value) + ' 원';
                            }
                        }
                    }
                }
            }
        });

        // 4. 기상 데이터 준비 (기상 그래프) - 캐시 사용 및 조건부 렌더링
        const currentBaseDate = document.getElementById('date-input-1').value;
        let weatherDatasets;
        if (weatherDataCache && cachedBaseDate === currentBaseDate) {
            // 캐시된 데이터가 있고 기준 날짜가 동일하면 캐시된 데이터 사용
            weatherDatasets = weatherDataCache;
            // 기상 차트가 이미 그려져 있고 데이터가 동일하면 다시 그리지 않음
            if (weatherChart) {
                return; // 여기서 함수 종료하여 기상 차트 새로고침 방지
            }
        } else {
            // 캐시된 데이터가 없거나 기준 날짜가 다르면 새로 생성
            const weatherColors = ['#4CAF50', '#2196F3', '#FFC107']; // 강수량, 습도, 기온 색상

            const rainfallData = []; // 강수량 (mm)
            const humidityData = []; // 습도 (%)
            const temperatureData = []; // 기온 (°C)

            for (let i = 0; i < totalDays; i++) { // 총 12일치 데이터 생성
                rainfallData.push(parseFloat((Math.random() * 10).toFixed(1))); // 0.0 ~ 10.0mm
                humidityData.push(Math.floor(Math.random() * (100 - 50) + 50)); // 50 ~ 100%
                temperatureData.push(parseFloat((Math.random() * (30 - 10) + 10).toFixed(1))); // 10.0 ~ 30.0°C
            }

            weatherDatasets = [
                {
                    label: '강수량 (mm)',
                    data: rainfallData,
                    borderColor: weatherColors[0],
                    backgroundColor: weatherColors[0] + '33',
                    fill: false,
                    tension: 0.2,
                    yAxisID: 'y-rainfall'
                },
                {
                    label: '습도 (%)',
                    data: humidityData,
                    borderColor: weatherColors[1],
                    backgroundColor: weatherColors[1] + '33',
                    fill: false,
                    tension: 0.2,
                    yAxisID: 'y-humidity'
                },
                {
                    label: '기온 (°C)',
                    data: temperatureData,
                    borderColor: weatherColors[2],
                    backgroundColor: weatherColors[2] + '33',
                    fill: false,
                    tension: 0.2,
                    yAxisID: 'y-temperature'
                }
            ];
            // 캐시 업데이트
            weatherDataCache = weatherDatasets;
            cachedBaseDate = currentBaseDate;
        }

        // 5. 기상 차트 생성/업데이트
        if (weatherChart) {
            weatherChart.destroy(); // 기존 차트가 있으면 제거
        }

        weatherChart = new Chart(weatherCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: weatherDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: '최근 1주일 예보 기상 정보'
                    }
                },
                scales: {
                    'y-rainfall': {
                        type: 'linear',
                        position: 'left',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '강수량 (mm)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                    'y-humidity': {
                        type: 'linear',
                        position: 'right',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '습도 (%)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                    'y-temperature': {
                        type: 'linear',
                        position: 'right',
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '기온 (°C)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }

    // 개수 선택 시 입력 필드 동적 생성
    itemCountSelect.addEventListener('change', (e) => {
        createInputFields(e.target.value);
        renderCharts(); // 입력 필드 변경 시 차트도 업데이트
    });

    // 예측 버튼 클릭 이벤트
    predictBtn.addEventListener('click', renderCharts);

    // 페이지 로드 시 기본값으로 필드 생성 및 차트 렌더링
    createInputFields(itemCountSelect.value);
    renderCharts();
});