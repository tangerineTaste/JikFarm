// app.py 에서 정의된 함수를 이용하여 값 변경 시 테이블 데이터 초기화

// 토글 모드: 'weekly' or 'daily'
document.addEventListener('DOMContentLoaded', function() {
let mode = 'weekly';

const form = document.getElementById('filter-form');
const modeDiv = document.createElement('div');
modeDiv.style.marginBottom = '10px';
modeDiv.innerHTML = `
    <button type="button" id="btn-weekly" class="active">주간</button>
    <button type="button" id="btn-daily">일간</button>
`;
form.prepend(modeDiv);

const weekInputs = `
    <label>시작 주차:
    <input type="text" id="start-week" name="start_week" placeholder="예: 202410" required>
    </label>
    <label>종료 주차:
    <input type="text" id="end-week" name="end_week" placeholder="예: 202423" required>
    </label>
`;
const dayInputs = `
    <label>시작일:
    <input type="date" id="start-date" name="start_date" required>
    </label>
    <label>종료일:
    <input type="date" id="end-date" name="end_date" required>
    </label>
`;

// 기간 필드 영역만 변경
function switchInputs(newMode) {
    const area = document.getElementById('period-fields');
    if (!area) return;
    area.innerHTML = (newMode === 'weekly') ? weekInputs : dayInputs;
}

// 버튼 클릭 시 모드/입력필드/드롭다운/테이블 초기화
modeDiv.querySelector('#btn-weekly').onclick = async function() {
    if (mode === 'weekly') return;
    mode = 'weekly';
    this.classList.add('active');
    modeDiv.querySelector('#btn-daily').classList.remove('active');
    switchInputs(mode);
    await fetchLatestWeeks();
    await fetchItems();
    await fetchVarieties();
    await fetchSanjis();
    setTableHeader();
    clearTable();
};
modeDiv.querySelector('#btn-daily').onclick = async function() {
    if (mode === 'daily') return;
    mode = 'daily';
    this.classList.add('active');
    modeDiv.querySelector('#btn-weekly').classList.remove('active');
    switchInputs(mode);
    await setRecentDates();
    await fetchItems();
    await fetchVarieties();
    await fetchSanjis();
    setTableHeader();
    clearTable();
};

// 품목 드롭다운 세팅
async function fetchItems() {
    const select = document.getElementById('item-select');
    const prevValue = select.value || '1201';
    const res = await fetch('/api/items');
    const items = await res.json();
    select.innerHTML = items.map(i =>
    `<option value="${i.item_code}" ${i.item_code === prevValue ? 'selected' : ''}>
        ${i.gds_mclsf_nm}
    </option>`
    ).join('');
}

// 품종 드롭다운 세팅
async function fetchVarieties() {
    const itemCode = document.getElementById('item-select').value;
    const select = document.getElementById('variety-select');
    const prevValue = select.value || '';
    let start, end;
    if (mode === 'weekly') {
    start = document.getElementById('start-week').value;
    end = document.getElementById('end-week').value;
    } else {
    start = document.getElementById('start-date').value.replaceAll('-','');
    end = document.getElementById('end-date').value.replaceAll('-','');
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

// 등급 드롭다운
async function fetchGrades() {
    const itemCode = document.getElementById('item-select').value;
    const cropFullCode = document.getElementById('variety-select').value;
    let start, end;
    if (mode === 'weekly') {
        start = document.getElementById('start-week').value;
        end = document.getElementById('end-week').value;
    } else {
        start = document.getElementById('start-date').value.replaceAll('-','');
        end = document.getElementById('end-date').value.replaceAll('-','');
    }
    if (!itemCode || !start || !end) return;

    let url = `/api/grades?item_code=${itemCode}&start_week=${start}&end_week=${end}`;
    if (cropFullCode) url += `&crop_full_code=${cropFullCode}`;
    const res = await fetch(url);
    const grades = await res.json();

    const select = document.getElementById('grade-select');
    const prevValue = select.value || '';
    select.innerHTML = `<option value="">전체</option>` +
    grades.map(g =>
        `<option value="${g}" ${g === prevValue ? 'selected' : ''}>${g}</option>`
    ).join('');
}


// 산지 드롭다운 세팅
async function fetchSanjis() {
    const itemCode = document.getElementById('item-select').value;
    const cropFullCode = document.getElementById('variety-select').value;
    const grade = document.getElementById('grade-select').value; 
    const select = document.getElementById('sanji-select');
    const prevValue = select.value || '';
    let start, end;
    if (mode === 'weekly') {
    start = document.getElementById('start-week').value;
    end = document.getElementById('end-week').value;
    } else {
    start = document.getElementById('start-date').value.replaceAll('-','');
    end = document.getElementById('end-date').value.replaceAll('-','');
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

// 테이블 헤더 세팅
function setTableHeader() {
    const thead = document.querySelector('#result-table thead');
    if (mode === 'weekly') {
    thead.innerHTML = `
        <tr>
        <th>주차</th><th>품목</th><th>품종</th><th>등급</th><th>산지</th><th>거래량(kg)</th><th>평균단가(원)</th>
        </tr>
    `;
    } else {
    thead.innerHTML = `
        <tr>
        <th>날짜</th><th>품목</th><th>품종</th><th>등급</th><th>산지</th><th>거래량(kg)</th><th>평균단가(원)</th>
        </tr>
    `;
    }
}
function clearTable() {
    document.querySelector('#result-table tbody').innerHTML = '';
}

// 입력값 변화 감지(폼 전체에 적용, 순서 제어)
form.addEventListener('change', async function(e) {
    if (
        e.target.id === 'item-select' ||
        e.target.id === 'start-week' ||
        e.target.id === 'end-week' ||
        e.target.id === 'start-date' ||
        e.target.id === 'end-date'
        ) {
        // 품목/기간 바뀌면: 품종 → 등급 → 산지 순서로
        await fetchVarieties();
        await fetchGrades();
        await fetchSanjis();
        }
        
    if (e.target.id === 'variety-select') {
        await fetchGrades();
        await fetchSanjis();
    }
    if (e.target.id === 'grade-select') {
        await fetchSanjis();
        }
});

// 조회(Submit) 시
form.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(form);
    const params = {};
    formData.forEach((value, key) => {
    if (value !== "") params[key] = value;
    });
    setTableHeader();
    if (mode === 'weekly') {
    fetchWeeklyTrade(params);
    } else {
    fetchDailyTrade(params);
    }
});

async function fetchWeeklyTrade(params) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`/api/weekly_trade?${query}`);
    const data = await res.json();
    const tbody = document.querySelector('#result-table tbody');
    if (!Array.isArray(data) || data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7">데이터 없음</td></tr>';
    return;
    }
    tbody.innerHTML = data.map(row => `
    <tr>
        <td>${row.weekno || '-'}</td>
        <td>${row.gds_mclsf_nm || '-'}</td>
        <td>${row.gds_sclsf_nm || '-'}</td>
        <td>${row.grd_nm || '-'}</td>
        <td>${row.j_sanji_nm || '-'}</td>
        <td>${row.unit_tot_qty || '-'}</td>
        <td>${row.avg_price || '-'}</td>
    </tr>
    `).join('');
}
async function fetchDailyTrade(params) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`/api/daily_trade?${query}`);
    const data = await res.json();
    const tbody = document.querySelector('#result-table tbody');
    if (!Array.isArray(data) || data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7">데이터 없음</td></tr>';
    return;
    }
    tbody.innerHTML = data.map(row => `
    <tr>
        <td>${row.trd_clcln_ymd || '-'}</td>
        <td>${row.gds_mclsf_nm || '-'}</td>
        <td>${row.gds_sclsf_nm || '-'}</td>
        <td>${row.grd_nm || '-'}</td>
        <td>${row.j_sanji_nm || '-'}</td>
        <td>${row.unit_tot_qty || '-'}</td>
        <td>${row.avg_price || '-'}</td>
    </tr>
    `).join('');
}

// 기간 입력 자동 초기화
async function fetchLatestWeeks() {
    const res = await fetch('/api/latest_weeks');
    const { start_week, end_week } = await res.json();
    if (document.getElementById('start-week')) document.getElementById('start-week').value = start_week;
    if (document.getElementById('end-week')) document.getElementById('end-week').value = end_week;
}
async function setRecentDates() {
    const res = await fetch('/api/latest_dates');
    const { start_date, end_date } = await res.json();
    if (document.getElementById('start-date')) document.getElementById('start-date').value = start_date;
    if (document.getElementById('end-date')) document.getElementById('end-date').value = end_date;
}

// 최초 실행
(async function init() {
    switchInputs(mode);
    setTableHeader();
    await fetchLatestWeeks();
    await fetchItems();
    await fetchVarieties();
    await fetchSanjis();
    // 최초 데이터 자동 조회
    setTimeout(() => {
    form.dispatchEvent(new Event('submit'));
    }, 200);
})();
});