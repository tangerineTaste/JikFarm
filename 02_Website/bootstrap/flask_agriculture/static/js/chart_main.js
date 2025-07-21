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
    const trendQueryBtn = document.getElementById('trend-query-btn');
    const cropSelect = document.getElementById('crop-select');
    const varietySelect = document.getElementById('variety-select');
    const gradeSelect = document.getElementById('grade-select');
    const originSelect = document.getElementById('origin-select');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const btnWeekly = document.getElementById('btn-weekly');
    const btnDaily = document.getElementById('btn-daily');
    let trendView = 'weekly'; // Default to weekly

    const periodFields = document.getElementById('period-fields');

    const weekInputs = `
        <label>시작 주차:</label>
        <input type="text" id="start-week" placeholder="예: 202410">
        <span>~</span>
        <label>종료 주차:</label>
        <input type="text" id="end-week" placeholder="예: 202423">
    `;

    const dayInputs = `
        <label>기간:</label>
        <input type="date" id="start-date">
        <span>~</span>
        <input type="date" id="end-date">
    `;

    // AI예측 elements
    const aiPredictBtn = document.getElementById('ai-predict-btn');
    const aiCropSelect = document.getElementById('ai-crop-select');
    const aiTermSelect = document.getElementById('ai-term-select');

    // 날짜(YYYY-MM-DD)를 주차(YYYYWW)로 변환하는 헬퍼 함수
    function getWeekNumberFromDate(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const firstDayOfYear = new Date(year, 0, 1);
        const days = Math.floor((date - firstDayOfYear) / (24 * 60 * 60 * 1000));
        // 간단한 주차 계산 (ISO 8601과 다를 수 있음, DB의 weekno 정의에 따라 조정 필요)
        const weekNumber = Math.ceil((days + firstDayOfYear.getDay() + 1) / 7);
        return `${year}${String(weekNumber).padStart(2, '0')}`;
    }

    // 탭 전환 로직
    function switchTab(tab) {
        if (tab === 'trend') {
            tabTrend.classList.add('active');
            tabAi.classList.remove('active');
            trendSection.style.display = 'block';
            aiSection.style.display = 'none';
            renderTrendChart(); // 탭 전환 시 차트 다시 그리기
        } else {
            tabAi.classList.add('active');
            tabTrend.classList.remove('active');
            aiSection.style.display = 'block';
            trendSection.style.display = 'none';
            renderAiPredictionChart(); // 탭 전환 시 차트 다시 그리기
        }
    }

    tabTrend.addEventListener('click', () => switchTab('trend'));
    tabAi.addEventListener('click', () => switchTab('ai'));

    // 초기 데이터 로딩
    async function loadInitialData() {
        try {
            // 주간/일간 모드에 따른 초기화
            await switchTrendView(trendView, true);

            // 품목 로딩
            const itemsResponse = await fetch('/api/items');
            const items = await itemsResponse.json();
            cropSelect.innerHTML = '';
            aiCropSelect.innerHTML = '';
            items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.item_code;
                option.textContent = item.gds_mclsf_nm;
                cropSelect.appendChild(option.cloneNode(true));
                aiCropSelect.appendChild(option);
            });

            // 초기 필터 데이터 로딩
            await fetchVarieties();
            await fetchGrades();
            await fetchSanjis();

            // 초기 차트 렌더링
            switchTab('trend');

        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    // 주간/일간 조회 모드 변경
    async function switchTrendView(newView, isInitialLoad = false) {
        trendView = newView;
        periodFields.innerHTML = trendView === 'weekly' ? weekInputs : dayInputs;

        if (trendView === 'weekly') {
            const weeksResponse = await fetch('/api/latest_weeks');
            const weeks = await weeksResponse.json();
            document.getElementById('start-week').value = weeks.start_week;
            document.getElementById('end-week').value = weeks.end_week;
        } else {
            const datesResponse = await fetch('/api/latest_dates');
            const dates = await datesResponse.json();
            document.getElementById('start-date').value = dates.start_date;
            document.getElementById('end-date').value = dates.end_date;
        }

        if (!isInitialLoad) {
            await fetchVarieties();
            await fetchGrades();
            await fetchSanjis();
            renderTrendChart();
        }
        setActiveTrendButton();
    }

    // 품종 동적 로딩
    async function fetchVarieties() {
        const itemCode = cropSelect.value;
        const select = varietySelect;
        const prevValue = select.value || '';
        let start, end;
        if (trendView === 'weekly') {
            start = document.getElementById('start-week').value;
            end = document.getElementById('end-week').value;
        } else {
            start = document.getElementById('start-date').value.replaceAll('-', '');
            end = document.getElementById('end-date').value.replaceAll('-', '');
        }
        if (!itemCode || !start || !end) {
            select.innerHTML = `<option value="">전체</option>`;
            return;
        }
        const res = await fetch(`/api/varieties?item_code=${itemCode}&start_week=${start}&end_week=${end}`);
        const varieties = await res.json();
        select.innerHTML = `<option value="">전체</option>` +
            varieties.map(v =>
                `<option value="${v.crop_full_code}" ${v.crop_full_code === prevValue ? 'selected' : ''}>
        ${v.gds_sclsf_nm}
        </option>`
            ).join('');
    }

    // 등급 동적 로딩
    async function fetchGrades() {
        const itemCode = cropSelect.value;
        const cropFullCode = varietySelect.value;
        const select = gradeSelect;
        const prevValue = select.value || '';
        let start, end;
        if (trendView === 'weekly') {
            start = document.getElementById('start-week').value;
            end = document.getElementById('end-week').value;
        } else {
            start = document.getElementById('start-date').value.replaceAll('-', '');
            end = document.getElementById('end-date').value.replaceAll('-', '');
        }
        if (!itemCode || !start || !end) {
            select.innerHTML = `<option value="">전체</option>`;
            return;
        }

        let url = `/api/grades?item_code=${itemCode}&start_week=${start}&end_week=${end}`;
        if (cropFullCode) url += `&crop_full_code=${cropFullCode}`;
        const res = await fetch(url);
        const grades = await res.json();

        select.innerHTML = `<option value="">전체</option>` +
            grades.map(g =>
                `<option value="${g}" ${g === prevValue ? 'selected' : ''}>${g}</option>`
            ).join('');
    }


    // 산지 동적 로딩
    async function fetchSanjis() {
        const itemCode = cropSelect.value;
        const cropFullCode = varietySelect.value;
        const grade = gradeSelect.value;
        const select = originSelect;
        const prevValue = select.value || '';
        let start, end;
        if (trendView === 'weekly') {
            start = document.getElementById('start-week').value;
            end = document.getElementById('end-week').value;
        } else {
            start = document.getElementById('start-date').value.replaceAll('-', '');
            end = document.getElementById('end-date').value.replaceAll('-', '');
        }
        if (!itemCode || !start || !end) {
            select.innerHTML = '<option value="">전체</option>';
            return;
        }
        let query = `?item_code=${itemCode}&start_week=${start}&end_week=${end}`;
        if (cropFullCode) query += `&crop_full_code=${cropFullCode}`;
        if (grade) query += `&grade=${grade}`;
        const res = await fetch(`/api/sanjis${query}`);
        const sanjis = await res.json();
        select.innerHTML = '<option value="">전체</option>' +
            sanjis.map(s =>
                `<option value="${s.j_sanji_cd}" ${s.j_sanji_cd === prevValue ? 'selected' : ''}>
        ${s.j_sanji_nm}
        </option>`
            ).join('');
    }

    // 트렌드 분석 로직 (API 연동)
    async function renderTrendChart() {
        setActiveTrendButton();
        const itemCode = cropSelect.value;
        const cropFullCode = varietySelect.value;
        const grade = gradeSelect.value;
        const sanjiCd = originSelect.value;

        if (!itemCode) {
            alert('품목을 선택해주세요.');
            return;
        }

        try {
            const apiPath = trendView === 'weekly' ? '/api/weekly_trade' : '/api/daily_trade';
            const params = new URLSearchParams({
                item_code: itemCode,
                ...(cropFullCode && { crop_full_code: cropFullCode }),
                ...(grade && { grade: grade }),
                ...(sanjiCd && { sanji_cd: sanjiCd }),
            });

            if (trendView === 'weekly') {
                params.append('start_week', document.getElementById('start-week').value);
                params.append('end_week', document.getElementById('end-week').value);
            } else {
                params.append('start_date', document.getElementById('start-date').value);
                params.append('end_date', document.getElementById('end-date').value);
            }

            const response = await fetch(`${apiPath}?${params.toString()}`);
            const data = await response.json();

            const labels = data.map(row => trendView === 'weekly' ? row.weekno : row.trd_clcln_ymd);
            const priceData = data.map(row => row.avg_price);
            const volumeData = data.map(row => row.unit_tot_qty);
            const chartTitle = `${cropSelect.options[cropSelect.selectedIndex].text} 가격 및 거래량 (${trendView === 'weekly' ? '주간' : '일간'})`;

            drawChart(labels, priceData, volumeData, cropSelect.options[cropSelect.selectedIndex].text, chartTitle);
            updateDataTable(labels, priceData, volumeData);

        } catch (error) {
            console.error('Error fetching trade data:', error);
            alert('데이터를 불러오는 데 실패했습니다. 콘솔을 확인해주세요.');
        }
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

    btnWeekly.addEventListener('click', () => switchTrendView('weekly'));
    btnDaily.addEventListener('click', () => switchTrendView('daily'));
    trendQueryBtn.addEventListener('click', renderTrendChart);

    // 필터 변경 감지
    cropSelect.addEventListener('change', async () => {
        await fetchVarieties();
        await fetchGrades();
        await fetchSanjis();
    });

    // 날짜 변경 감지 (이벤트 위임 사용)
    periodFields.addEventListener('change', async (e) => {
        if (e.target.matches('#start-week, #end-week, #start-date, #end-date')) {
            await fetchVarieties();
            await fetchGrades();
            await fetchSanjis();
        }
    });

    varietySelect.addEventListener('change', async () => {
        await fetchGrades();
        await fetchSanjis();
    });

    gradeSelect.addEventListener('change', fetchSanjis);

    // AI예측 로직 (임시 데이터 사용)
    function renderAiPredictionChart() {
        const selectedCrop = aiCropSelect.value;
        const termDays = parseInt(aiTermSelect.value, 10);

        const labels = [];
        const historicalData = [];
        const predictionData = [];

        // 임시 데이터 생성 (실제 API 연동 필요)
        const baseDate = new Date();
        for (let i = 7; i > 0; i--) { // 과거 7일
            const date = new Date(baseDate);
            date.setDate(baseDate.getDate() - i);
            labels.push(date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }));
            historicalData.push(3000 + Math.random() * 500);
        }

        for (let i = 0; i < termDays; i++) { // 예측 기간
            const date = new Date(baseDate);
            date.setDate(baseDate.getDate() + i);
            labels.push(date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }));
            predictionData.push(null);
        }
        
        const fullPriceData = historicalData.concat(predictionData);
        const predictionLine = new Array(historicalData.length - 1).fill(null);
        let lastHistoricalValue = historicalData[historicalData.length - 1];
        for(let i = 0; i < termDays + 1; i++) {
             predictionLine.push(lastHistoricalValue + (Math.random() - 0.5) * 200 * i);
        }

        const volumeData = fullPriceData.map(() => Math.random() * 5000 + 10000);
        const chartTitle = `${aiCropSelect.options[aiCropSelect.selectedIndex].text} AI 예측 결과`;
        drawAiChart(labels, fullPriceData, predictionLine, volumeData, aiCropSelect.options[aiCropSelect.selectedIndex].text, chartTitle);
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
    loadInitialData();
});