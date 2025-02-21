//write.html-이미지 업로드
document.addEventListener('DOMContentLoaded', function() {

    const uploadContainer = document.querySelector('.image-upload-container');
    const fileInput = document.getElementById('bouquet-upload');
    const previewImage = document.getElementById('preview-image');
    const uploadPlaceholder = document.querySelector('.upload-placeholder');

    // 파일 선택 시 프리뷰
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.classList.remove('hidden');
                uploadPlaceholder.classList.add('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    // 드래그 앤 드롭 기능
    uploadContainer.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    uploadContainer.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });

    uploadContainer.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.classList.remove('hidden');
                uploadPlaceholder.classList.add('hidden');
            };
            reader.readAsDataURL(file);
        }
    });
});

//write.html-검색
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const bouquetUpload = document.getElementById('bouquet-upload');
    const previewImage = document.getElementById('preview-image');
    const selectedFlowers = new Map();
 // done-write 버튼
    const doneWriteBtn = document.querySelector('#done-write');
     if (doneWriteBtn) {
        doneWriteBtn.addEventListener('click', async function() {
            try {
                // 이미지 파일 가져오기
                const fileInput = document.getElementById('bouquet-upload');
                const imageFile = fileInput.files[0];

                // FormData 객체 생성
                const formData = new FormData();
                if (imageFile) {
                    formData.append('file', imageFile);
                }

                // 이미지 먼저 업로드
                if (imageFile) {
                    await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                }

                // 선택된 꽃 정보 전송
                const response = await fetch('/api/selected-flowers', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(Array.from(selectedFlowers.values()))
                });

                if (response.ok) {
                    window.location.href = '/result';
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    }

    // Handle image upload and preview
    bouquetUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.classList.remove('hidden');
                document.querySelector('.upload-placeholder').classList.add('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle search input
    let debounceTimer;
    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = e.target.value.trim();
            if (query.length > 0) {
                searchFlowers(query);
            } else {
                searchResults.innerHTML = '';
            }
        }, 300);
    });

    // Search flowers function
    async function searchFlowers(query) {
        try {
            const response = await fetch(`/api/search/${encodeURIComponent(query)}`);
            const flowers = await response.json();
            displayResults(flowers);
        } catch (error) {
            console.error('Error searching flowers:', error);
        }
    }

      function displayResults(flowers) {
        searchResults.innerHTML = '';

        flowers.forEach(flower => {
            const flowerElement = document.createElement('div');
            flowerElement.className = 'flower-item';
            // 이미 선택된 꽃인 경우 selected 클래스 추가
            if (selectedFlowers.has(flower.index)) {
                flowerElement.classList.add('selected');
            }

            flowerElement.innerHTML = `
                <img src="/static/honest/${flower.image}.jpg" alt="${flower.name_kr}" class="flower-thumbnail">
                <div class="flower-info">
                    <h3 class="flower-name">${flower.name_kr}</h3>
                    <p class="flower-description">${flower.name_en} / ${flower.mean}</p>
                </div>
            `;

            // 클릭 이벤트 수정
            flowerElement.addEventListener('click', function() {
                this.classList.toggle('selected');

                if (this.classList.contains('selected')) {
                    selectedFlowers.set(flower.index, flower);
                } else {
                    selectedFlowers.delete(flower.index);
                }
            });

            searchResults.appendChild(flowerElement);
        });

        if (flowers.length === 0) {
            searchResults.innerHTML = '<div class="no-results">검색 결과가 없습니다.</div>';
        }
    }
});

//result.html
document.addEventListener('DOMContentLoaded', async function() {
    const flowerList = document.querySelector('.flower-list');

    try {
        // 서버에서 선택된 꽃 정보 가져오기
        const response = await fetch('/api/selected-flowers');
        const selectedFlowers = await response.json();

        // 꽃 목록 표시
        selectedFlowers.forEach(flower => {
            const flowerElement = document.createElement('div');
            flowerElement.className = 'flower-item';

            flowerElement.innerHTML = `
                <img src="/static/honest/${flower.image}.jpg" alt="${flower.name_kr}" class="flower-thumbnail">
                <div class="flower-info">
                    <h3 class="flower-name">${flower.name_kr}</h3>
                    <p class="flower-description">${flower.name_en} / ${flower.mean}</p>
                </div>
            `;

            flowerList.appendChild(flowerElement);
        });
    } catch (error) {
        console.error('Error loading selected flowers:', error);
    }
});