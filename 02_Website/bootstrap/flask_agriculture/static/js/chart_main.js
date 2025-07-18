document.addEventListener('DOMContentLoaded', function() {
    // Common elements
    const priceCtx = document.getElementById('price-chart').getContext('2d');
    let priceChart = null;

    // Tab elements
    const tabTrend = document.getElementById('tab-trend');
    const tabAi = document.getElementById('tab-ai');
    const trendSection = document.getElementById('trend-analysis-section');
    const aiSection = document.getElementById('ai-prediction-section');

    // 트렌드 분석 elements
    const trendQueryBtn = document.querySelector('#trend-analysis-section .query-button');
    const cropSelect = document.getElementById('crop-select');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const btnWeekly = document.getElementById('btn-weekly');
    const btnDaily = document.getElementById('btn-daily');
    let trendView = 'weekly';

    // AI예측 elements
    const aiPredictBtn = document.getElementById('ai-predict-btn');
    const aiCropSelect = document.getElementById('ai-crop-select');
    
    const aiTermSelect = document.getElementById('ai-term-select');

    // 기본날짜 설정
    const today = new Date();
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(today.getMonth() - 1);
    startDateInput.valueAsDate = oneMonthAgo;
    endDateInput.valueAsDate = today;

    // 탭 전환 로직
    function switchTab(tab) {
        if (tab === 'trend') {
            tabTrend.classList.add('active');
            tabAi.classList.remove('active');
            trendSection.style.display = 'block';
            aiSection.style.display = 'none';
            renderTrendChart();
        } else {
            tabAi.classList.add('active');
            tabTrend.classList.remove('active');
            aiSection.style.display = 'block';
            trendSection.style.display = 'none';
            renderAiPredictionChart();
        }
    }

    tabTrend.addEventListener('click', () => switchTab('trend'));
    tabAi.addEventListener('click', () => switchTab('ai'));

    // 트렌드 분석 로직
    function renderTrendChart() {
        setActiveTrendButton(); // 트렌드 분석탭이 기본적으로 활성화
        const selectedCrop = cropSelect.value;
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);

        let labels = [];
        let priceData = [];

        if (trendView === 'weekly') {
            let currentDate = new Date(startDate);
            while (currentDate <= endDate) {
                const weekNumber = Math.ceil(currentDate.getDate() / 7);
                const month = currentDate.getMonth() + 1;
                labels.push(`${month}월 ${weekNumber}주차`);
                priceData.push(3000 + Math.random() * 500);
                currentDate.setDate(currentDate.getDate() + 7);
            }
        } else { // 일간 보기
            let currentDate = new Date(startDate);
            while (currentDate <= endDate) {
                labels.push(currentDate.toLocaleDateString('ko-KR', { month: 'long', day: 'numeric' }));
                priceData.push(3000 + Math.random() * 500);
                currentDate.setDate(currentDate.getDate() + 1);
            }
        }

        const volumeData = priceData.map(() => Math.random() * 5000 + 10000);
        const chartTitle = `${selectedCrop} 가격 및 거래량 (${trendView === 'weekly' ? '주간' : '일간'})`;
        drawChart(labels, priceData, volumeData, selectedCrop, chartTitle);
        updateDataTable(labels, priceData, volumeData);
    }

    function setActiveTrendButton() {
        if (trendView === 'weekly') {
            btnWeekly.classList.add('active');
            btnDaily.classList.remove('active');
        } else {
            btnDaily.classList.add('active');
            btnWeekly.classList.remove('active');
        }
    }

    btnWeekly.addEventListener('click', () => {
        trendView = 'weekly';
        setActiveTrendButton();
        renderTrendChart();
    });
    btnDaily.addEventListener('click', () => {
        trendView = 'daily';
        setActiveTrendButton();
        renderTrendChart();
    });
    trendQueryBtn.addEventListener('click', renderTrendChart);

    // AI예측 로직
    function renderAiPredictionChart() {
        const selectedCrop = aiCropSelect.value;
        const baseDate = new Date(); // Always start from today
        const termDays = parseInt(aiTermSelect.value, 10);

        const labels = [];
        const historicalData = [];
        const predictionData = [];

        // 오늘 날짜로부터 3일 이전까지의 무작위 데이터 생성
        for (let i = 3; i > 0; i--) {
            const date = new Date(baseDate);
            date.setDate(baseDate.getDate() - i);
            labels.push(date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }));
            historicalData.push(3000 + Math.random() * 500);
        }

        // 예측 데이터 생성
        for (let i = 0; i < termDays; i++) {
            const date = new Date(baseDate);
            date.setDate(baseDate.getDate() + i);
            labels.push(date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }));
            predictionData.push(null); // Placeholder for prediction
        }
        
        const fullPriceData = historicalData.concat(predictionData);
        // 예측 데이터의 시작점을 위에서 생성한 데이터로 만들어준다.
        const predictionLine = new Array(historicalData.length - 1).fill(null);
        let lastHistoricalValue = historicalData[historicalData.length - 1];
        for(let i = 0; i < termDays + 1; i++) {
             predictionLine.push(lastHistoricalValue + (Math.random() - 0.5) * 200 * i);
        }

        const volumeData = fullPriceData.map(() => Math.random() * 5000 + 10000);
        const chartTitle = `${selectedCrop} AI 예측 결과`;
        drawAiChart(labels, fullPriceData, predictionLine, volumeData, selectedCrop, chartTitle);
        updateDataTable(labels, fullPriceData, volumeData);
    }

    aiPredictBtn.addEventListener('click', renderAiPredictionChart);

    // 차트 그리기 함수
    function getChartOptions(chartTitle) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: chartTitle
                }
            },
            scales: {
                y: { // 주간 가격 차트의 주요 Y축
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('ko-KR').format(value) + ' 원';
                        }
                    },
                    title: {
                        display: true,
                        text: '가격 (원)'
                    }
                },
                y1: { // 주간 거래량 차트의 주요 Y축
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false, // 주요 축의 그리드만 그리기
                    },
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('ko-KR').format(value);
                        }
                    },
                    title: {
                        display: true,
                        text: '거래량'
                    }
                }
            }
        };
    }

    function drawChart(labels, priceData, volumeData, title, chartTitle) {
        if (priceChart) priceChart.destroy();
        priceChart = new Chart(priceCtx, {
            data: {
                labels: labels,
                datasets: [
                    { type: 'line', label: `${title} 가격`, data: priceData, yAxisID: 'y', borderColor: '#28a745', backgroundColor: 'rgba(40, 167, 69, 0.1)', tension: 0.4 },
                    { type: 'bar', label: `${title} 거래량`, data: volumeData, yAxisID: 'y1', backgroundColor: 'rgba(153, 102, 255, 0.2)' }
                ]
            },
            options: getChartOptions(chartTitle)
        });
    }
    
    function drawAiChart(labels, priceData, predictionLine, volumeData, title, chartTitle) {
        if (priceChart) priceChart.destroy();
        priceChart = new Chart(priceCtx, {
            data: {
                labels: labels,
                datasets: [
                    { type: 'line', label: `${title} 과거 가격`, data: priceData, yAxisID: 'y', borderColor: '#28a745', fill: false, tension: 0.4 },
                    { type: 'line', label: `${title} 예측 가격`, data: predictionLine, yAxisID: 'y', borderColor: '#8A2BE2', borderDash: [5, 5], fill: false, tension: 0.4 },
                    { type: 'bar', label: `${title} 거래량`, data: volumeData, yAxisID: 'y1', backgroundColor: 'rgba(153, 102, 255, 0.2)' }
                ]
            },
            options: getChartOptions(chartTitle)
        });
    }

    function updateDataTable(labels, priceData, volumeData) {
        const tableBody = document.getElementById('price-data-table');
        tableBody.innerHTML = '';
        labels.forEach((label, index) => {
            const row = document.createElement('tr');
            const price = priceData[index] ? new Intl.NumberFormat('ko-KR').format(priceData[index].toFixed(0)) : 'N/A';
            const volume = volumeData[index] ? new Intl.NumberFormat('ko-KR').format(volumeData[index].toFixed(0)) : 'N/A';
            row.innerHTML = `<td>${label}</td><td>${price}</td><td>${volume}</td>`;
            tableBody.appendChild(row);
        });
    }

    // Initial Load
    switchTab('trend');
});