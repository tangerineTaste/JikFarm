document.addEventListener('DOMContentLoaded', function() {
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
                alert(result.message);
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
});