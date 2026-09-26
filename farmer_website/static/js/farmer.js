// Farmer Portal Main JavaScript Logic

document.addEventListener('DOMContentLoaded', () => {
    checkFarmerAuth();
    loadFarmerHarvests();
    loadFarmerStats();
});

// Auth Helpers
function openAuthModal(mode) {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.remove('hidden');
        toggleAuthMode(mode);
    }
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.add('hidden');
}

function toggleAuthMode(mode) {
    const loginForm = document.getElementById('loginForm');
    const regForm = document.getElementById('registerForm');
    const title = document.getElementById('modalTitle');
    
    if (mode === 'register') {
        loginForm.classList.add('hidden');
        regForm.classList.remove('hidden');
        if (title) title.innerText = 'Register as Farmer';
    } else {
        regForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
        if (title) title.innerText = 'Farmer Login';
    }
}

async function handleAuthLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role: 'farmer' })
        });
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('user_id', data.user.id);
            localStorage.setItem('user_role', data.user.role);
            localStorage.setItem('user_name', data.user.name);
            window.location.href = '/farmer/dashboard';
        } else {
            alert(data.message || 'Login failed.');
        }
    } catch (err) {
        console.error(err);
        alert('Error connecting to server.');
    }
}

async function handleAuthRegister(e) {
    e.preventDefault();
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const city = document.getElementById('regCity').value;
    const state = document.getElementById('regState').value;
    const password = document.getElementById('regPassword').value;
    
    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, city, state, password, role: 'farmer' })
        });
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('user_id', data.user.id);
            localStorage.setItem('user_role', data.user.role);
            localStorage.setItem('user_name', data.user.name);
            window.location.href = '/farmer/dashboard';
        } else {
            alert(data.message || 'Registration failed.');
        }
    } catch (err) {
        console.error(err);
        alert('Error creating account.');
    }
}

function quickDemoLogin() {
    localStorage.setItem('user_id', '1');
    localStorage.setItem('user_role', 'farmer');
    localStorage.setItem('user_name', 'Shaik Basha (Farmer)');
    window.location.href = '/farmer/dashboard';
}

function handleLogout() {
    fetch('/api/auth/logout').finally(() => {
        localStorage.clear();
        window.location.href = '/farmer';
    });
}

function checkFarmerAuth() {
    const userName = localStorage.getItem('user_name') || 'Shaik Basha';
    const navName = document.getElementById('navUserName');
    const dashName = document.getElementById('dashFarmerName');
    if (navName) navName.innerText = userName;
    if (dashName) dashName.innerText = userName;
}

// Tab Switching
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
    
    const activeBtn = document.getElementById(`tabBtn-${tabId}`);
    const activeContent = document.getElementById(`tab-${tabId}`);
    
    if (activeBtn) activeBtn.classList.add('active');
    if (activeContent) activeContent.classList.remove('hidden');
}

// ==============================================================================
// AI LEAF DISEASE SCANNER LOGIC
// ==============================================================================
let selectedLeafFile = null;

function previewLeafImage(input) {
    if (input.files && input.files[0]) {
        selectedLeafFile = input.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('dropzoneContent').classList.add('hidden');
            const container = document.getElementById('imagePreviewContainer');
            container.classList.remove('hidden');
            document.getElementById('previewImg').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function loadSampleImage(type) {
    const cropSelect = document.getElementById('diseaseCropSelect');
    const previewContainer = document.getElementById('imagePreviewContainer');
    const dropzoneContent = document.getElementById('dropzoneContent');
    const previewImg = document.getElementById('previewImg');
    
    dropzoneContent.classList.add('hidden');
    previewContainer.classList.remove('hidden');

    if (type === 'tomato_early') {
        cropSelect.value = 'Tomato';
        previewImg.src = 'https://images.unsplash.com/photo-1592417817098-8f3d6eb22509?w=500';
    } else if (type === 'potato_blight') {
        cropSelect.value = 'Potato';
        previewImg.src = 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500';
    } else if (type === 'powdery_mildew') {
        cropSelect.value = 'Vegetables & Cucurbits';
        previewImg.src = 'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500';
    }
}

async function handleDiseaseSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('btnScanDisease');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing with Deep Learning...';
    btn.disabled = true;
    
    const crop = document.getElementById('diseaseCropSelect').value;
    const formData = new FormData();
    formData.append('crop', crop);
    formData.append('farmer_id', localStorage.getItem('user_id') || 1);
    
    if (selectedLeafFile) {
        formData.append('image', selectedLeafFile);
    }
    
    try {
        const res = await fetch('/api/ai/disease-detection', {
            method: 'POST',
            body: formData
        });
        const json = await res.json();
        
        if (json.success) {
            renderDiseaseResult(json.data);
        } else {
            alert('Error running disease model: ' + json.message);
        }
    } catch (err) {
        console.error(err);
        alert('Diagnostic service error.');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function renderDiseaseResult(data) {
    document.getElementById('diseasePlaceholder').classList.add('hidden');
    document.getElementById('diseaseActiveResult').classList.remove('hidden');
    
    document.getElementById('resCropName').innerText = `Crop: ${data.crop}`;
    document.getElementById('resDiseaseName').innerText = data.disease;
    document.getElementById('resConfidence').innerText = `${data.confidence}%`;
    document.getElementById('resSymptoms').innerText = data.symptoms;
    document.getElementById('resSafety').innerText = data.safe_application_info;
    
    // Organic List
    const orgList = document.getElementById('resOrganicList');
    orgList.innerHTML = '';
    data.organic_recommendations.forEach(item => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-2';
        li.innerHTML = `<i class="fa-solid fa-check text-emerald-600 mt-1"></i> <span>${item}</span>`;
        orgList.appendChild(li);
    });

    // Chemical List
    const chemList = document.getElementById('resChemicalList');
    chemList.innerHTML = '';
    data.chemical_recommendations.forEach(item => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-2';
        li.innerHTML = `<i class="fa-solid fa-check text-blue-600 mt-1"></i> <span>${item}</span>`;
        chemList.appendChild(li);
    });

    // Recommended Product & Direct BUY NOW button linking to Buyer Website
    if (data.recommended_product) {
        document.getElementById('resProductName').innerText = data.recommended_product.name;
        document.getElementById('resProductPrice').innerText = `₹${data.recommended_product.price.toFixed(2)} / ${data.recommended_product.unit}`;
        
        // Pass product_id and session seamlessly to buyer website
        const buyBtn = document.getElementById('btnBuyNowProduct');
        buyBtn.href = `/buyer?product_id=${data.recommended_product.id}&source=farmer_ai#product-${data.recommended_product.id}`;
    }
}


// ==============================================================================
// AI CROP RECOMMENDER LOGIC
// ==============================================================================
async function handleCropRecSubmit(e) {
    e.preventDefault();
    const payload = {
        n: document.getElementById('recN').value,
        p: document.getElementById('recP').value,
        k: document.getElementById('recK').value,
        temp: document.getElementById('recTemp').value,
        humidity: document.getElementById('recHumidity').value,
        ph: document.getElementById('recPh').value,
        rainfall: document.getElementById('recRainfall').value,
        farmer_id: localStorage.getItem('user_id') || 1
    };

    try {
        const res = await fetch('/api/ai/crop-recommendation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
            renderCropRecResult(json.data);
        }
    } catch (err) {
        console.error(err);
        alert('Crop recommendation error.');
    }
}

function renderCropRecResult(data) {
    document.getElementById('cropRecPlaceholder').classList.add('hidden');
    document.getElementById('cropRecActiveResult').classList.remove('hidden');

    const top = data.primary_recommendation;
    document.getElementById('topRecCrop').innerText = top.crop;
    document.getElementById('topRecConfidence').innerText = `${top.confidence}%`;
    document.getElementById('topRecYield').innerText = top.yield_acre;
    document.getElementById('topRecDuration').innerText = top.duration;
    document.getElementById('topRecRoi').innerText = `${top.roi_percent}%`;
    document.getElementById('topRecSeason').innerText = top.season;

    const altList = document.getElementById('recAlternativesList');
    altList.innerHTML = '';
    data.alternatives.forEach(alt => {
        const div = document.createElement('div');
        div.className = 'p-4 rounded-2xl bg-slate-50 border border-slate-200';
        div.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <strong class="text-sm font-bold text-slate-800">${alt.crop}</strong>
                <span class="text-xs font-bold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full">${alt.confidence}% Match</span>
            </div>
            <div class="text-xs text-slate-600 space-y-1">
                <div>Yield: <strong>${alt.yield_acre}</strong></div>
                <div>Duration: <strong>${alt.duration}</strong></div>
                <div>Soil: <strong>${alt.soil_type}</strong></div>
            </div>
        `;
        altList.appendChild(div);
    });
}


// ==============================================================================
// SOIL & FERTILIZER ADVISOR LOGIC
// ==============================================================================
async function handleFertilizerSubmit(e) {
    e.preventDefault();
    const payload = {
        crop: document.getElementById('fertCrop').value,
        n: document.getElementById('fertN').value,
        p: document.getElementById('fertP').value,
        k: document.getElementById('fertK').value,
        ph: document.getElementById('fertPh').value,
        acres: document.getElementById('fertAcres').value
    };

    try {
        const res = await fetch('/api/ai/soil-fertilizer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
            renderFertilizerResult(json.data);
        }
    } catch (err) {
        console.error(err);
        alert('Fertilizer advisor error.');
    }
}

function renderFertilizerResult(data) {
    document.getElementById('fertPlaceholder').classList.add('hidden');
    document.getElementById('fertActiveResult').classList.remove('hidden');

    document.getElementById('fertDeficitSummary').innerText = 
        `N Deficit: ${data.deficit.n} kg | P Deficit: ${data.deficit.p} kg | K Deficit: ${data.deficit.k} kg`;

    const orgList = document.getElementById('fertOrganicSchedule');
    orgList.innerHTML = '';
    data.organic_schedule.forEach(s => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-2';
        li.innerHTML = `<i class="fa-solid fa-leaf text-emerald-600 mt-1"></i> <span>${s}</span>`;
        orgList.appendChild(li);
    });

    const chemList = document.getElementById('fertChemicalSchedule');
    chemList.innerHTML = '';
    data.chemical_schedule.forEach(s => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-2';
        li.innerHTML = `<i class="fa-solid fa-flask text-blue-600 mt-1"></i> <span>${s}</span>`;
        chemList.appendChild(li);
    });
}


// ==============================================================================
// SMART IRRIGATION LOGIC
// ==============================================================================
async function handleIrrigationSubmit(e) {
    e.preventDefault();
    const payload = {
        crop: document.getElementById('irrigCrop').value,
        stage: document.getElementById('irrigStage').value,
        soil: document.getElementById('irrigSoil').value,
        acres: document.getElementById('irrigAcres').value
    };

    try {
        const res = await fetch('/api/ai/irrigation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
            document.getElementById('resIrrigLitres').innerText = 
                `${json.data.water_required_litres_per_day.toLocaleString()} Litres / Day`;
        }
    } catch (err) {
        console.error(err);
    }
}


// ==============================================================================
// MY HARVESTS & SELL MY CROP (Farmer -> Seller Workflow)
// ==============================================================================
function openSellCropModal() {
    const modal = document.getElementById('sellCropModal');
    if (modal) modal.classList.remove('hidden');
}

function closeSellCropModal() {
    const modal = document.getElementById('sellCropModal');
    if (modal) modal.classList.add('hidden');
}

async function handleSellCropSubmit(e) {
    e.preventDefault();
    const payload = {
        farmer_id: localStorage.getItem('user_id') || 1,
        crop_name: document.getElementById('sellCropName').value,
        variety: document.getElementById('sellVariety').value,
        quantity: document.getElementById('sellQuantity').value,
        expected_price_per_unit: document.getElementById('sellPrice').value,
        quality: document.getElementById('sellQuality').value,
        harvest_date: document.getElementById('sellDate').value,
        location: document.getElementById('sellLocation').value,
        description: document.getElementById('sellDescription').value
    };

    try {
        const res = await fetch('/api/harvests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
            alert('🎉 ' + json.message);
            closeSellCropModal();
            loadFarmerHarvests();
            switchTab('harvests');
        } else {
            alert(json.message);
        }
    } catch (err) {
        console.error(err);
        alert('Error submitting harvest.');
    }
}

async function loadFarmerHarvests() {
    const grid = document.getElementById('harvestsListGrid');
    if (!grid) return;

    try {
        const farmerId = localStorage.getItem('user_id') || 1;
        const res = await fetch(`/api/harvests?farmer_id=${farmerId}`);
        const json = await res.json();
        
        if (json.success) {
            grid.innerHTML = '';
            if (json.harvests.length === 0) {
                grid.innerHTML = '<div class="col-span-2 text-center py-10 text-slate-400 text-sm">No harvest listings posted yet. Click "Post New Harvest" to sell produce.</div>';
                return;
            }

            json.harvests.forEach(h => {
                const isPurchased = (h.status === 'purchased_by_seller');
                const card = document.createElement('div');
                card.className = 'bg-slate-50 rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between';
                card.innerHTML = `
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="px-2.5 py-1 rounded-full text-xs font-bold ${isPurchased ? 'bg-blue-100 text-blue-800' : 'bg-emerald-100 text-emerald-800'}">
                                ${isPurchased ? ' Purchased by Seller' : ' Live for Agribusiness Sellers'}
                            </span>
                            <span class="text-xs text-slate-400 font-semibold">${h.harvest_date}</span>
                        </div>
                        <h4 class="text-lg font-bold text-slate-900">${h.crop_name} (${h.variety || 'Standard'})</h4>
                        <div class="grid grid-cols-2 gap-2 my-3 text-xs text-slate-600 bg-white p-3 rounded-xl border border-slate-200">
                            <div>Quantity: <strong class="text-slate-900">${h.quantity} ${h.unit}</strong></div>
                            <div>Expected Price: <strong class="text-emerald-700">₹${h.expected_price_per_unit} / ${h.unit}</strong></div>
                            <div>Quality Grade: <strong class="text-slate-900">${h.quality}</strong></div>
                            <div>Location: <strong class="text-slate-900">${h.location}</strong></div>
                        </div>
                        <p class="text-xs text-slate-500 mb-4">${h.description || 'Farm-gate direct harvest.'}</p>
                    </div>
                    <div class="pt-3 border-t border-slate-200 text-xs font-semibold flex items-center justify-between text-slate-500">
                        <span>Status: <strong class="${isPurchased ? 'text-blue-600' : 'text-emerald-600'}">${h.status.replace('_', ' ').toUpperCase()}</strong></span>
                        <a href="/seller#farmer-harvests" class="text-blue-600 hover:underline">View in Seller Feed &rarr;</a>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

async function loadFarmerStats() {
    try {
        const farmerId = localStorage.getItem('user_id') || 1;
        const res = await fetch(`/api/farmer/stats?user_id=${farmerId}`);
        const json = await res.json();
        if (json.success && document.getElementById('statHarvests')) {
            document.getElementById('statHarvests').innerText = `${json.stats.active_harvests} Listings`;
        }
    } catch (err) {
        console.error(err);
    }
}


// ==============================================================================
// AGRIBOT CHATBOT LOGIC
// ==============================================================================
async function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;

    const chatBox = document.getElementById('chatMessages');
    
    // Append User message
    const userDiv = document.createElement('div');
    userDiv.className = 'flex items-start gap-2.5 max-w-[85%] ml-auto justify-end';
    userDiv.innerHTML = `
        <div class="p-3 bg-emerald-600 text-white rounded-2xl rounded-tr-none shadow-sm text-xs leading-relaxed">
            ${msg}
        </div>
        <div class="w-7 h-7 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center text-xs flex-shrink-0">
            <i class="fa-solid fa-user"></i>
        </div>
    `;
    chatBox.appendChild(userDiv);
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Call API
    try {
        const res = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });
        const json = await res.json();
        
        // Append Bot response
        const botDiv = document.createElement('div');
        botDiv.className = 'flex items-start gap-2.5 max-w-[85%]';
        botDiv.innerHTML = `
            <div class="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs flex-shrink-0">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="p-3 bg-white rounded-2xl rounded-tl-none border border-slate-200 shadow-sm text-slate-700 leading-relaxed text-xs">
                ${json.reply}
            </div>
        `;
        chatBox.appendChild(botDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        console.error(err);
    }
}

// Audio Readout Functions for Illiterate Farmers
function speakDiseaseResult() {
    if (!window.voiceLangMgr) return;
    const crop = document.getElementById('resCropName')?.innerText || '';
    const disease = document.getElementById('resDiseaseName')?.innerText || '';
    const confidence = document.getElementById('resConfidence')?.innerText || '';
    const symptoms = document.getElementById('resSymptoms')?.innerText || '';
    const product = document.getElementById('resProductName')?.innerText || '';
    
    const textToSpeak = `${crop}. Disease diagnosed: ${disease} with ${confidence} accuracy. Symptoms: ${symptoms}. Recommended treatment product: ${product}. Click Buy Now to order.`;
    window.voiceLangMgr.speakText(textToSpeak);
}

function speakCropRecResult() {
    if (!window.voiceLangMgr) return;
    const crop = document.getElementById('topRecCrop')?.innerText || '';
    const match = document.getElementById('topRecConfidence')?.innerText || '';
    const yieldAcre = document.getElementById('topRecYield')?.innerText || '';
    const duration = document.getElementById('topRecDuration')?.innerText || '';
    const roi = document.getElementById('topRecRoi')?.innerText || '';

    const textToSpeak = `Top recommended crop for your soil is ${crop} with ${match} confidence. Expected yield is ${yieldAcre}, crop duration is ${duration}, estimated return on investment is ${roi}.`;
    window.voiceLangMgr.speakText(textToSpeak);
}


