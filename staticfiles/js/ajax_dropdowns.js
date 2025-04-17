document.addEventListener('DOMContentLoaded', function() {
    // Region -> Division
    document.getElementById('id_police_region').addEventListener('change', function() {
        const regionId = this.value;
        const divisionSelect = document.getElementById('id_division');
        const districtSelect = document.getElementById('id_district');
        const stationSelect = document.getElementById('id_station');

        if (!regionId) {
            divisionSelect.innerHTML = '<option value="">--------- Select Division ---------</option>';
            districtSelect.innerHTML = '<option value="">--------- Select District ---------</option>';
            stationSelect.innerHTML = '<option value="">--------- Select Station ---------</option>';
            return;
        }

        fetch(`{% url 'ajax-load-divisions' %}?region_id=${regionId}`)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.text();
            })
            .then(html => {
                divisionSelect.innerHTML = html;
                divisionSelect.disabled = false;
                divisionSelect.dispatchEvent(new Event('change'));
            })
            .catch(error => {
                console.error('Error loading divisions:', error);
                divisionSelect.innerHTML = '<option value="">Error loading divisions</option>';
            });
    });

    // Division -> District
    document.getElementById('id_division').addEventListener('change', function() {
        const divisionId = this.value;
        const districtSelect = document.getElementById('id_district');
        const stationSelect = document.getElementById('id_station');

        if (!divisionId) {
            districtSelect.innerHTML = '<option value="">--------- Select District ---------</option>';
            stationSelect.innerHTML = '<option value="">--------- Select Station ---------</option>';
            return;
        }

        fetch(`{% url 'ajax-load-districts' %}?division_id=${divisionId}`)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.text();
            })
            .then(html => {
                districtSelect.innerHTML = html;
                districtSelect.disabled = false;
                districtSelect.dispatchEvent(new Event('change'));
            })
            .catch(error => {
                console.error('Error loading districts:', error);
                districtSelect.innerHTML = '<option value="">Error loading districts</option>';
            });
    });

    // District -> Station
    document.getElementById('id_district').addEventListener('change', function() {
        const districtId = this.value;
        const stationSelect = document.getElementById('id_station');

        if (!districtId) {
            stationSelect.innerHTML = '<option value="">--------- Select Station ---------</option>';
            return;
        }

        fetch(`{% url 'ajax-load-policestations' %}?district_id=${districtId}`)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.text();
            })
            .then(html => {
                stationSelect.innerHTML = html;
                stationSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error loading stations:', error);
                stationSelect.innerHTML = '<option value="">Error loading stations</option>';
            });
    });
});