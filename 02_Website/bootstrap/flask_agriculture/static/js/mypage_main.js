document.addEventListener('DOMContentLoaded', function() {
    // ... (기존 관심 품목 코드)

    // 회원 정보 수정 관련 로직
    const editProfileBtn = document.getElementById('edit-profile-btn');
    const modal = document.getElementById('edit-profile-modal');
    const closeBtn = document.querySelector('.close-btn');
    const editProfileForm = document.getElementById('edit-profile-form');

    // 현재 정보로 폼 채우기
    function populateEditForm() {
        document.getElementById('edit-nickname').value = document.getElementById('user-nickname').textContent;
        document.getElementById('edit-name').value = document.getElementById('user-name').textContent;
    }

    // 모달 열기
    editProfileBtn.addEventListener('click', () => {
        populateEditForm();
        modal.style.display = 'block';
    });

    // 모달 닫기
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    // 정보 수정 제출
    editProfileForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(editProfileForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/update_profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                // UI 업데이트
                document.getElementById('user-nickname').textContent = result.nickname;
                document.getElementById('user-name').textContent = result.name;
                // 헤더의 닉네임도 업데이트 (만약 헤더에 닉네임 표시 부분이 있다면)
                const headerNickname = document.querySelector('.user-nickname-display'); // 예시 선택자
                if(headerNickname) headerNickname.textContent = result.nickname + '님';
                
                modal.style.display = 'none';
                alert('정보가 성공적으로 수정되었습니다.');
            } else {
                alert('오류: ' + result.error);
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            alert('프로필 업데이트 중 오류가 발생했습니다.');
        }
    });
});

    const interestCropsContainer = document.getElementById('interest-crops-container');
    const saveInterestCropsBtn = document.getElementById('save-interest-crops-btn');

    let allAvailableCrops = [];

    async function loadInterestCrops() {
        try {
            // Fetch all available crops
            const availableCropsResponse = await fetch('/api/interest_crops');
            allAvailableCrops = await availableCropsResponse.json();

            // Fetch member's current interest crops
            const memberCropsResponse = await fetch('/api/member_interest_crops');
            const memberCrops = await memberCropsResponse.json();

            renderCheckboxes(allAvailableCrops, memberCrops);

        } catch (error) {
            console.error('Error loading interest crops:', error);
            alert('관심 품목을 불러오는 데 실패했습니다.');
        }
    }

    function renderCheckboxes(availableCrops, memberCrops) {
        interestCropsContainer.innerHTML = '';
        availableCrops.forEach(crop => {
            const isChecked = memberCrops.includes(crop.crop_id);
            const colDiv = document.createElement('div');
            colDiv.className = 'col-lg-3 col-md-4 col-sm-6'; // Adjust column classes as needed
            colDiv.innerHTML = `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${crop.crop_id}" id="crop-${crop.crop_id}" ${isChecked ? 'checked' : ''}>
                    <label class="form-check-label" for="crop-${crop.crop_id}">
                        ${crop.display_name}
                    </label>
                </div>
            `;
            interestCropsContainer.appendChild(colDiv);
        });
    }

    saveInterestCropsBtn.addEventListener('click', async function() {
        const selectedCropIds = [];
        interestCropsContainer.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
            selectedCropIds.push(checkbox.value);
        });

        try {
            const response = await fetch('/api/save_member_interest_crops', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ crop_ids: selectedCropIds }),
            });

            const result = await response.json();

            if (response.ok) {
                alert('관심 품목을 변경하였습니다.');
            } else {
                alert('관심 품목 저장 실패: ' + result.error);
            }
        } catch (error) {
            console.error('Error saving interest crops:', error);
            alert('관심 품목 저장 중 오류가 발생했습니다.');
        }
    });

    // Initial load
    loadInterestCrops();
