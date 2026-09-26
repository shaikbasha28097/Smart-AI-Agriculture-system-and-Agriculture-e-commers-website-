// Seller Agribusiness Main JavaScript Logic

document.addEventListener('DOMContentLoaded', () => {
    checkSellerAuth();
    loadSellerFarmerHarvests();
    loadSellerInventory();
    loadSellerOrders();
    initSellerCharts();
});

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
        if (title) title.innerText = 'Register Agribusiness';
    } else {
        regForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
        if (title) title.innerText = 'Seller Login';
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
            body: JSON.stringify({ email, password, role: 'seller' })
        });
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('user_id', data.user.id);
            localStorage.setItem('user_role', data.user.role);
            localStorage.setItem('user_name', data.user.name);
            window.location.href = '/seller/dashboard';
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
    const password = document.getElementById('regPassword').value;
    
    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, city, password, role: 'seller' })
        });
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('user_id', data.user.id);
            localStorage.setItem('user_role', data.user.role);
            localStorage.setItem('user_name', data.user.name);
            window.location.href = '/seller/dashboard';
        } else {
            alert(data.message || 'Registration failed.');
        }
    } catch (err) {
        console.error(err);
        alert('Error creating account.');
    }
}

function quickDemoLogin() {
    localStorage.setItem('user_id', '2');
    localStorage.setItem('user_role', 'seller');
    localStorage.setItem('user_name', 'ABC Agro Traders (Seller)');
    window.location.href = '/seller/dashboard';
}

function handleLogout() {
    fetch('/api/auth/logout').finally(() => {
        localStorage.clear();
        window.location.href = '/seller';
    });
}

function checkSellerAuth() {
    const userName = localStorage.getItem('user_name') || 'ABC Agro Traders';
    const navName = document.getElementById('navSellerName');
    const dashName = document.getElementById('dashSellerName');
    if (navName) navName.innerText = userName;
    if (dashName) dashName.innerText = userName;
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
    
    const activeBtn = document.getElementById(`tabBtn-${tabId}`);
    const activeContent = document.getElementById(`tab-${tabId}`);
    
    if (activeBtn) activeBtn.classList.add('active');
    if (activeContent) activeContent.classList.remove('hidden');
}


// ==============================================================================
// 1. AVAILABLE FARMER CROPS FEED (Farmer -> Seller Workflow)
// ==============================================================================
async function loadSellerFarmerHarvests() {
    const feed = document.getElementById('farmerHarvestsFeed');
    if (!feed) return;

    try {
        const res = await fetch('/api/seller/farmer-harvests');
        const json = await res.json();
        
        if (json.success) {
            feed.innerHTML = '';
            let availableCount = 0;

            json.harvests.forEach(h => {
                const isPurchased = (h.status === 'purchased_by_seller');
                if (!isPurchased) availableCount++;

                const card = document.createElement('div');
                card.className = `p-5 rounded-2xl border ${isPurchased ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-900 border-slate-700 shadow-md'} flex flex-col justify-between`;
                card.innerHTML = `
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="px-2.5 py-1 rounded-full text-xs font-bold ${isPurchased ? 'bg-slate-800 text-slate-400' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}">
                                ${isPurchased ? '✓ Acquired / In Inventory' : '⚡ Available for Sourcing'}
                            </span>
                            <span class="text-xs text-slate-400 font-semibold">${h.harvest_date}</span>
                        </div>

                        <h4 class="text-base font-bold text-white mb-1">${h.crop_name} (${h.variety || 'Standard'})</h4>
                        
                        <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1.5 my-3 text-xs">
                            <div class="flex justify-between"><span class="text-slate-400">Grower / Farmer:</span> <strong class="text-white">${h.farmer_name}</strong></div>
                            <div class="flex justify-between"><span class="text-slate-400">Location:</span> <strong class="text-white">${h.location}</strong></div>
                            <div class="flex justify-between"><span class="text-slate-400">Total Lot Quantity:</span> <strong class="text-emerald-400">${h.quantity} ${h.unit}</strong></div>
                            <div class="flex justify-between"><span class="text-slate-400">Expected Farm-Gate:</span> <strong class="text-blue-300 font-bold">₹${h.expected_price_per_unit} / ${h.unit}</strong></div>
                            <div class="flex justify-between"><span class="text-slate-400">Quality Standard:</span> <strong class="text-amber-300">${h.quality}</strong></div>
                        </div>

                        <p class="text-xs text-slate-400 mb-4">${h.description || 'Farm-gate direct harvest.'}</p>
                    </div>

                    <div>
                        ${isPurchased ? `
                            <button disabled class="w-full py-2.5 rounded-xl bg-slate-800 text-slate-500 font-bold text-xs cursor-not-allowed">
                                Already Acquired
                            </button>
                        ` : `
                            <button onclick="acquireFarmerHarvest(${h.id}, '${h.crop_name}', ${h.quantity}, '${h.unit}')" class="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-600/30 transition flex items-center justify-center gap-2">
                                <i class="fa-solid fa-handshake"></i> 1-Click Purchase / Acquire Lot
                            </button>
                        `}
                    </div>
                `;
                feed.appendChild(card);
            });

            const statCrops = document.getElementById('statFarmerCrops');
            if (statCrops) statCrops.innerText = `${availableCount} Lots Available`;
        }
    } catch (err) {
        console.error(err);
    }
}

async function acquireFarmerHarvest(harvestId, cropName, quantity, unit) {
    if (!confirm(`Confirm acquisition of ${quantity} ${unit} ${cropName} from farmer?`)) return;

    try {
        const sellerId = localStorage.getItem('user_id') || 2;
        const res = await fetch(`/api/seller/buy-harvest/${harvestId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seller_id: sellerId })
        });
        const json = await res.json();
        
        if (json.success) {
            alert('🎉 ' + json.message);
            loadSellerFarmerHarvests();
            loadSellerInventory();
        } else {
            alert(json.message);
        }
    } catch (err) {
        console.error(err);
        alert('Error acquiring crop.');
    }
}


// Global scan state for seller
let currentSellerScanPreset = 'organic';
let currentModalScanPreset = 'organic';
let currentModalChemPct = 12.4;
let currentModalIsRejected = false;
let lastApprovedScanData = null;

// ==============================================================================
// 2. AI WHOLE-LOT QUALITY & CHEMICAL INSPECTOR (Seller Tab)
// ==============================================================================
function updateSellerScanPresets() {
    const cat = document.getElementById('sellerScanCategory').value;
    const commInput = document.getElementById('sellerScanCommodity');
    if (!commInput) return;
    
    if (cat === '1') commInput.value = 'Mango';
    else if (cat === '2') commInput.value = 'Tomato';
    else if (cat === '3') commInput.value = 'Hybrid Tomato Seeds';
    else if (cat === '4') commInput.value = 'Mango Live Sapling';
}

function setSellerScanPreset(type) {
    currentSellerScanPreset = type;
    const btnOrg = document.getElementById('btnPresetOrganic');
    const btnChem = document.getElementById('btnPresetChemical');
    
    if (type === 'organic') {
        if (btnOrg) btnOrg.className = 'px-3 py-2 rounded-xl bg-emerald-600/50 border-2 border-emerald-400 text-emerald-200 text-xs font-bold transition text-left';
        if (btnChem) btnChem.className = 'px-3 py-2 rounded-xl bg-red-600/20 border border-red-500/30 text-red-300 text-xs font-bold transition text-left';
    } else {
        if (btnOrg) btnOrg.className = 'px-3 py-2 rounded-xl bg-emerald-600/20 border border-emerald-500/30 text-emerald-300 text-xs font-bold transition text-left';
        if (btnChem) btnChem.className = 'px-3 py-2 rounded-xl bg-red-600/50 border-2 border-red-400 text-red-200 text-xs font-bold transition text-left';
    }
}

async function runSellerWholeLotScan() {
    const btn = document.getElementById('btnRunSellerScan');
    const resultBox = document.getElementById('sellerScanResultBox');
    const commodity = document.getElementById('sellerScanCommodity').value || 'Tomato';
    const category_id = document.getElementById('sellerScanCategory').value || 1;
    const imageInput = document.getElementById('sellerScanImage');

    if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing Whole Lot Chemical & TDS Matrix...';

    const formData = new FormData();
    formData.append('commodity', commodity);
    formData.append('category_id', category_id);
    formData.append('sample_type', currentSellerScanPreset);

    if (imageInput && imageInput.files.length > 0) {
        formData.append('image', imageInput.files[0]);
    }

    try {
        const res = await fetch('/api/ai/scan-product-lot', {
            method: 'POST',
            body: formData
        });
        const json = await res.json();

        if (json.success) {
            renderSellerScanResults(json.data);
        } else {
            alert(json.message || 'Inspection error.');
        }
    } catch (err) {
        console.error(err);
        alert('Server connection error during quality scan.');
    } finally {
        if (btn) btn.innerHTML = '<i class="fa-solid fa-microchip"></i> Scan Whole Lot & Verify Selling Eligibility';
    }
}

function previewScanLotImage(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            const container = document.getElementById('scanLotPreviewContainer');
            const img = document.getElementById('scanLotPreviewImg');
            const name = document.getElementById('scanLotFileName');
            if (container) container.classList.remove('hidden');
            if (img) img.src = e.target.result;
            if (name) name.innerText = file.name;
        };
        reader.readAsDataURL(file);
    }
}

function previewProdModalImage(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            const box = document.getElementById('prodImagePreviewBox');
            const img = document.getElementById('prodImagePreview');
            const placeholder = document.getElementById('prodImagePlaceholder');
            if (box) box.classList.remove('hidden');
            if (img) img.src = e.target.result;
            if (placeholder) placeholder.classList.add('hidden');
            currentModalCustomImageUrl = null;
        };
        reader.readAsDataURL(file);
    }
}

let currentModalCustomImageUrl = null;

function renderSellerScanResults(data) {
    const box = document.getElementById('sellerScanResultBox');
    if (!box) return;

    lastApprovedScanData = data;
    const isRejected = data.is_rejected;
    const chemPct = data.chemical_percentage;
    const qualityScore = data.quality_score;
    const displayImg = data.image_url || 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500';

    box.innerHTML = `
        <div class="space-y-4 animate-fadeIn">
            <!-- Selling Condition Banner with Scanned Photo Thumbnail -->
            <div class="p-4 rounded-2xl ${isRejected ? 'bg-red-500/20 border-2 border-red-500' : 'bg-emerald-500/20 border-2 border-emerald-500'} flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                <div class="flex items-center gap-3.5">
                    <img src="${displayImg}" class="w-16 h-16 rounded-xl object-cover border-2 ${isRejected ? 'border-red-400' : 'border-emerald-400'} shadow" alt="Scanned Produce">
                    <div>
                        <div class="flex items-center gap-2 mb-0.5">
                            <span class="text-lg">${isRejected ? '❌' : '✅'}</span>
                            <h4 class="text-sm font-extrabold ${isRejected ? 'text-red-400' : 'text-emerald-400'}">
                                ${isRejected ? 'LOT REJECTED (> 30% Chemical)' : 'LOT APPROVED FOR E-MART'}
                            </h4>
                        </div>
                        <p class="text-xs ${isRejected ? 'text-red-200' : 'text-emerald-200'} font-medium">
                            ${data.selling_message}
                        </p>
                    </div>
                </div>
                <span class="px-3 py-1 rounded-full text-xs font-black uppercase whitespace-nowrap ${isRejected ? 'bg-red-600 text-white shadow-lg' : 'bg-emerald-600 text-white shadow-lg'}">
                    ${data.selling_status}
                </span>
            </div>

            <!-- Quantitative Metrics Grid -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div class="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-center">
                    <span class="text-[10px] uppercase font-bold text-slate-400 block mb-1">Chemical Residue</span>
                    <strong class="text-xl font-black ${chemPct > 30 ? 'text-red-400' : 'text-emerald-400'}">${chemPct}%</strong>
                    <span class="text-[9px] text-slate-500 block">Max Limit: 30.0%</span>
                </div>
                <div class="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-center">
                    <span class="text-[10px] uppercase font-bold text-slate-400 block mb-1">Quality Purity</span>
                    <strong class="text-xl font-black text-blue-400">${qualityScore}%</strong>
                    <span class="text-[9px] text-slate-500 block">Cell Health</span>
                </div>
                <div class="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-center">
                    <span class="text-[10px] uppercase font-bold text-slate-400 block mb-1">TDS Mineral Score</span>
                    <strong class="text-lg font-bold text-amber-400">${data.tds_score} <span class="text-[10px]">mg/L</span></strong>
                    <span class="text-[9px] text-slate-500 block">Safe Electrolytes</span>
                </div>
                <div class="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-center">
                    <span class="text-[10px] uppercase font-bold text-slate-400 block mb-1">Batch Uniformity</span>
                    <strong class="text-lg font-bold text-indigo-400">${data.batch_homogeneity_pct}%</strong>
                    <span class="text-[9px] text-slate-500 block">${data.lot_sample_tested}</span>
                </div>
            </div>

            <!-- Detailed Diagnostics Table -->
            <div class="p-4 bg-slate-950/70 rounded-xl border border-slate-800 space-y-2 text-xs">
                <div class="flex justify-between border-b border-slate-800 pb-1.5"><span class="text-slate-400">Target Lot Sample:</span> <strong class="text-white">${data.commodity} (${data.category})</strong></div>
                <div class="flex justify-between border-b border-slate-800 pb-1.5"><span class="text-slate-400">Synthetic Contamination:</span> <strong class="${isRejected ? 'text-red-400' : 'text-emerald-400'}">${data.pesticide_detected}</strong></div>
                <div class="flex justify-between border-b border-slate-800 pb-1.5"><span class="text-slate-400">Ripening / Processing:</span> <strong class="text-white">${data.ripening_mode}</strong></div>
                <div class="flex justify-between border-b border-slate-800 pb-1.5"><span class="text-slate-400">Surface Wax / Glaze:</span> <strong class="text-white">${data.wax_coating}</strong></div>
                <div class="flex justify-between"><span class="text-slate-400">Toxicity Classification:</span> <strong class="text-amber-300">${data.toxicity_class}</strong></div>
            </div>

            <!-- 1-Click Action to Publish to E-Mart -->
            <div class="pt-2 space-y-2">
                ${!isRejected ? `
                    <button onclick="instantPublishToEMart()" id="btnInstantPublish" class="w-full py-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:from-emerald-500 hover:to-teal-600 text-white font-extrabold text-sm shadow-xl shadow-emerald-900/40 transition flex items-center justify-center gap-2 transform hover:-translate-y-0.5">
                        <i class="fa-solid fa-rocket text-amber-300"></i> Approve & Publish Directly to E-Mart (${data.category}) &rarr;
                    </button>
                    <button onclick="openPublishWithScanData('${data.commodity}', ${data.category_id}, ${chemPct})" class="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs border border-slate-700 transition flex items-center justify-center gap-2">
                        <i class="fa-solid fa-sliders"></i> Customize Price & Stock Before Listing
                    </button>
                ` : `
                    <button disabled class="w-full py-3 rounded-xl bg-slate-800 text-slate-500 font-bold text-xs cursor-not-allowed flex items-center justify-center gap-2">
                        <i class="fa-solid fa-ban text-red-500"></i> Selling Prohibited (> 30% Chemical Contamination)
                    </button>
                `}
            </div>
        </div>
    `;
}

function showSellerToast(title, message, viewUrl) {
    const existing = document.getElementById('sellerGlobalToast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'sellerGlobalToast';
    toast.className = 'fixed top-20 right-6 z-50 bg-slate-900 text-white px-6 py-4 rounded-2xl shadow-2xl border-2 border-emerald-500 flex items-start gap-3.5 max-w-md animate-bounce';
    toast.innerHTML = `
        <div class="w-9 h-9 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-lg flex-shrink-0">
            <i class="fa-solid fa-circle-check"></i>
        </div>
        <div class="flex-1 min-w-0">
            <h5 class="text-xs font-black text-emerald-400 uppercase tracking-wider">${title}</h5>
            <p class="text-xs text-slate-300 mt-0.5">${message}</p>
            ${viewUrl ? `
                <div class="mt-2.5 flex items-center gap-2">
                    <a href="${viewUrl}" target="_blank" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] inline-flex items-center gap-1.5 shadow transition">
                        <i class="fa-solid fa-arrow-up-right-from-square"></i> Preview on E-Mart ↗
                    </a>
                    <button onclick="switchTab('inventory'); document.getElementById('sellerGlobalToast')?.remove();" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-[11px] transition">
                        View Inventory
                    </button>
                </div>
            ` : ''}
        </div>
        <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white text-sm ml-1">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;
    document.body.appendChild(toast);
    setTimeout(() => { if (toast) toast.remove(); }, 8000);
}

async function instantPublishToEMart() {
    if (!lastApprovedScanData || lastApprovedScanData.is_rejected) {
        alert('Cannot publish a rejected lot.');
        return;
    }

    const btn = document.getElementById('btnInstantPublish');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Publishing Approved Product to Buyer E-Mart...';
    }

    const payload = {
        seller_id: localStorage.getItem('user_id') || 2,
        name: lastApprovedScanData.commodity,
        category_id: lastApprovedScanData.category_id || 1,
        price: lastApprovedScanData.default_price || 45.0,
        stock_quantity: lastApprovedScanData.default_stock || 150,
        unit: lastApprovedScanData.default_unit || 'KG',
        image_url: lastApprovedScanData.image_url,
        is_organic: lastApprovedScanData.is_organic ? 1 : 0,
        sample_type: currentSellerScanPreset,
        chemical_percentage: lastApprovedScanData.chemical_percentage,
        short_description: lastApprovedScanData.short_description || `AI Quality Certified (${lastApprovedScanData.chemical_percentage}% Chemical).`,
        description: `Verified safe produce lot inspected by AI Chemical Scanner. Chemical involvement: ${lastApprovedScanData.chemical_percentage}% (Within <= 30% safe threshold). TDS: ${lastApprovedScanData.tds_score} mg/L. Ripening: ${lastApprovedScanData.ripening_mode}.`
    };

    try {
        const res = await fetch('/api/seller/create-product', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();

        if (json.success) {
            // Refresh inventory grid
            loadSellerInventory();

            // Update button state on current screen
            if (btn) {
                btn.className = 'w-full py-3.5 rounded-2xl bg-emerald-950/80 border border-emerald-500 text-emerald-300 font-bold text-sm flex items-center justify-center gap-2';
                btn.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400"></i> Published Directly to E-Mart (${lastApprovedScanData.category || 'Produce'})!`;
            }

            // Show Toast notification with preview link
            const categoryNames = { 1: 'Fruits', 2: 'Vegetables', 3: 'Seeds', 4: 'Plants' };
            const catName = categoryNames[payload.category_id] || 'E-Mart';
            showSellerToast(
                `Product Published to E-Mart!`,
                `<strong>${payload.name}</strong> has passed AI inspection (&le; 30% Chemical) and is directly live in the <strong>${catName}</strong> category on Agri E-Mart.`,
                `/buyer?product_id=${json.product_id}#product-${json.product_id}`
            );
        } else {
            alert('⚠️ ' + (json.message || 'Error publishing product.'));
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-rocket text-amber-300"></i> Approve & Publish Directly to E-Mart &rarr;';
            }
        }
    } catch (err) {
        console.error(err);
        alert('Server error while publishing to Buyer E-Mart.');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-rocket text-amber-300"></i> Approve & Publish Directly to E-Mart &rarr;';
        }
    }
}

function openPublishWithScanData(commodityName, categoryId, chemPct) {
    openPublishProductModal();
    const nameEl = document.getElementById('prodName');
    const catEl = document.getElementById('prodCategory');
    if (nameEl) nameEl.value = commodityName;
    if (catEl) catEl.value = categoryId;
    handleModalCategoryChange();
    setModalScanPreset('organic');

    if (lastApprovedScanData && lastApprovedScanData.image_url) {
        currentModalCustomImageUrl = lastApprovedScanData.image_url;
        const box = document.getElementById('prodImagePreviewBox');
        const img = document.getElementById('prodImagePreview');
        const placeholder = document.getElementById('prodImagePlaceholder');
        if (box) box.classList.remove('hidden');
        if (img) img.src = lastApprovedScanData.image_url;
        if (placeholder) placeholder.classList.add('hidden');
    }
}



// ==============================================================================
// 3. INVENTORY & PUBLISH TO BUYER E-MART
// ==============================================================================
function openPublishProductModal() {
    const modal = document.getElementById('publishProductModal');
    if (modal) {
        modal.classList.remove('hidden');
        handleModalCategoryChange();
        
        // Reset image picker
        const imgInput = document.getElementById('prodImageInput');
        if (imgInput) imgInput.value = '';
        const box = document.getElementById('prodImagePreviewBox');
        if (box) box.classList.add('hidden');
        const placeholder = document.getElementById('prodImagePlaceholder');
        if (placeholder) placeholder.classList.remove('hidden');
        currentModalCustomImageUrl = null;
    }
}

function closePublishProductModal() {
    const modal = document.getElementById('publishProductModal');
    if (modal) modal.classList.add('hidden');
}

function handleModalCategoryChange() {
    const cat = document.getElementById('prodCategory').value;
    const inspSection = document.getElementById('modalInspectionSection');
    const unitContainer = document.getElementById('modalUnitContainer');
    const unitInput = document.getElementById('prodUnit');
    const stockRow = document.getElementById('modalStockAndUnitRow');
    
    // If Farming Tools (Category 8) is selected, do NOT display unit of measure
    if (cat === '8') {
        if (unitContainer) unitContainer.classList.add('hidden');
        if (unitInput) unitInput.value = '';
        if (stockRow) {
            stockRow.classList.remove('grid-cols-2');
            stockRow.classList.add('grid-cols-1');
        }
    } else {
        if (unitContainer) unitContainer.classList.remove('hidden');
        if (stockRow) {
            stockRow.classList.remove('grid-cols-1');
            stockRow.classList.add('grid-cols-2');
        }
        if (unitInput && (!unitInput.value || unitInput.value.trim() === '')) {
            if (cat === '9') unitInput.value = '1 KG Pack';
            else if (cat === '6' || cat === '7') unitInput.value = '1 KG Pack';
            else if (cat === '5') unitInput.value = '10 KG Bag';
            else if (cat === '4') unitInput.value = 'Live Plant';
            else if (cat === '3') unitInput.value = 'Pack of 10g';
            else unitInput.value = 'KG';
        }
    }

    // Categories 1 (Fruits), 2 (Vegetables), 3 (Seeds), 4 (Plants) require Whole-Lot Inspection
    if (['1', '2', '3', '4'].includes(cat)) {
        if (inspSection) inspSection.classList.remove('hidden');
        updateModalVerdict();
    } else {
        if (inspSection) inspSection.classList.add('hidden');
        clearModalRejection();
    }
}

function handleProdNameChange() {
    updateModalVerdict();
}

function setModalScanPreset(type) {
    currentModalScanPreset = type;
    const btnOrg = document.getElementById('modalPresetOrganic');
    const btnChem = document.getElementById('modalPresetChemical');

    if (type === 'organic') {
        currentModalChemPct = 12.4;
        currentModalIsRejected = false;
        if (btnOrg) btnOrg.className = 'py-1.5 px-2.5 rounded-lg bg-emerald-600 border border-emerald-400 text-white text-xs font-bold text-center transition';
        if (btnChem) btnChem.className = 'py-1.5 px-2.5 rounded-lg bg-red-600/20 border border-red-500/30 text-red-300 text-xs font-semibold text-center transition';
    } else {
        currentModalChemPct = 68.5;
        currentModalIsRejected = true;
        if (btnOrg) btnOrg.className = 'py-1.5 px-2.5 rounded-lg bg-emerald-600/20 border border-emerald-500/30 text-emerald-300 text-xs font-semibold text-center transition';
        if (btnChem) btnChem.className = 'py-1.5 px-2.5 rounded-lg bg-red-600 border border-red-400 text-white text-xs font-bold text-center transition';
    }
    updateModalVerdict();
}

function updateModalVerdict() {
    const cat = document.getElementById('prodCategory').value;
    if (!['1', '2', '3', '4'].includes(cat)) {
        clearModalRejection();
        return;
    }

    const statusText = document.getElementById('verdictStatusText');
    const detailText = document.getElementById('verdictDetailText');
    const badge = document.getElementById('verdictBadge');
    const errAlert = document.getElementById('publishErrorAlert');
    const errText = document.getElementById('publishErrorText');
    const submitBtn = document.getElementById('btnPublishSubmit');

    if (currentModalIsRejected || currentModalChemPct > 30.0) {
        if (statusText) statusText.className = 'font-bold text-red-400';
        if (statusText) statusText.innerText = '❌ FAILED: Chemical Residue > 30%';
        if (detailText) detailText.innerText = `Detected Chemical Residue: ${currentModalChemPct}% (Above 30% Threshold)`;
        if (badge) {
            badge.className = 'px-2 py-1 rounded bg-red-500/30 text-red-300 font-bold text-[10px]';
            badge.innerText = 'REJECTED';
        }
        if (errAlert) errAlert.classList.remove('hidden');
        if (errText) errText.innerText = `Listing REJECTED: Whole-lot chemical contamination is ${currentModalChemPct}%. Only products with <= 30% chemical involvement are approved for sale.`;
        if (submitBtn) {
            submitBtn.className = 'w-full py-3.5 rounded-xl bg-red-800/60 border border-red-700 text-red-200 font-bold text-sm cursor-not-allowed flex items-center justify-center gap-2';
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-ban text-red-400"></i> Rejected: Exceeds 30% Chemical Limit';
        }
    } else {
        if (statusText) statusText.className = 'font-bold text-emerald-400';
        if (statusText) statusText.innerText = '✅ APPROVED: Meets <= 30% Safe Quality Standard';
        if (detailText) detailText.innerText = `Detected Chemical Residue: ${currentModalChemPct}% (<= 30% Approved Safe Limit)`;
        if (badge) {
            badge.className = 'px-2 py-1 rounded bg-emerald-500/20 text-emerald-400 font-bold text-[10px]';
            badge.innerText = 'APPROVED';
        }
        if (errAlert) errAlert.classList.add('hidden');
        if (submitBtn) {
            submitBtn.className = 'w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2';
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-check-circle"></i> Publish Live on Buyer Website';
        }
    }
}

function clearModalRejection() {
    const errAlert = document.getElementById('publishErrorAlert');
    const submitBtn = document.getElementById('btnPublishSubmit');
    if (errAlert) errAlert.classList.add('hidden');
    if (submitBtn) {
        submitBtn.className = 'w-full py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-check-circle"></i> Publish Live on Buyer Website';
    }
}

async function handlePublishProductSubmit(e) {
    e.preventDefault();
    const cat = document.getElementById('prodCategory').value;

    // Strict Gatekeeper Check (Must be <= 30.0%)
    if (['1', '2', '3', '4'].includes(cat) && (currentModalIsRejected || currentModalChemPct > 30.0)) {
        alert(`❌ CANNOT PUBLISH PRODUCT!\n\nWhole-lot chemical contamination is ${currentModalChemPct}% (Exceeds 30% allowable limit).\nOnly products with 30% or lower chemical involvement are permitted to be sold on E-Mart.`);
        return;
    }

    const btn = document.getElementById('btnPublishSubmit');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Publishing to Buyer E-Mart...';
    }

    const prodName = document.getElementById('prodName').value;
    const formData = new FormData();
    formData.append('seller_id', localStorage.getItem('user_id') || 2);
    formData.append('name', prodName);
    formData.append('category_id', cat);
    formData.append('price', document.getElementById('prodPrice').value);
    formData.append('stock_quantity', document.getElementById('prodStock').value);
    formData.append('unit', document.getElementById('prodUnit').value);
    formData.append('is_organic', document.getElementById('prodIsOrganic').checked ? '1' : '0');
    formData.append('sample_type', currentModalScanPreset);
    formData.append('chemical_percentage', currentModalChemPct);
    formData.append('short_description', document.getElementById('prodDesc').value);
    formData.append('description', document.getElementById('prodDesc').value);

    if (currentModalCustomImageUrl) {
        formData.append('image_url', currentModalCustomImageUrl);
    }

    const imgInput = document.getElementById('prodImageInput');
    if (imgInput && imgInput.files.length > 0) {
        formData.append('image', imgInput.files[0]);
    }

    try {
        const res = await fetch('/api/seller/create-product', {
            method: 'POST',
            body: formData
        });
        const json = await res.json();
        if (json.success) {
            closePublishProductModal();
            loadSellerInventory();
            
            const categoryNames = { 1: 'Fruits', 2: 'Vegetables', 3: 'Seeds', 4: 'Plants', 5: 'Soil', 6: 'Organic Fertilizers', 7: 'Chemical Fertilizers', 8: 'Farming Tools', 9: 'Groceries' };
            const catName = categoryNames[cat] || 'E-Mart';
            
            showSellerToast(
                `Product Published to E-Mart!`,
                `<strong>${prodName}</strong> is now live in the <strong>${catName}</strong> category on Agri E-Mart with your uploaded photo & details.`,
                `/buyer?product_id=${json.product_id}#product-${json.product_id}`
            );
        } else {
            alert('⚠️ ' + (json.message || 'Product listing rejected by inspection server.'));
        }

    } catch (err) {
        console.error(err);
        alert('Error publishing product.');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-check-circle"></i> Publish Live on Buyer Website';
        }
    }
}

async function loadSellerInventory() {
    const grid = document.getElementById('inventoryGrid');
    if (!grid) return;

    try {
        const sellerId = localStorage.getItem('user_id') || 2;
        const res = await fetch(`/api/seller/inventory?seller_id=${sellerId}`);
        const json = await res.json();
        
        if (json.success) {
            grid.innerHTML = '';
            json.products.forEach(p => {
                const card = document.createElement('div');
                card.className = 'p-4 rounded-2xl bg-slate-900 border border-slate-700/80 shadow-sm flex flex-col justify-between';
                
                const isTool = (p.category_id == 8 || (p.category_name && p.category_name.toLowerCase().includes('tool')));
                const stockText = isTool ? `Stock: ${p.stock_quantity}` : `Stock: ${p.stock_quantity} ${p.unit || 'KG'}`;
                const priceText = isTool ? `₹${(Number(p.price) || 0).toFixed(2)}` : `₹${(Number(p.price) || 0).toFixed(2)} <span class="text-xs text-slate-400">/${p.unit || 'KG'}</span>`;

                card.innerHTML = `
                    <div>
                        <img src="${p.image_url}" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500';" class="w-full h-32 object-cover rounded-xl mb-3 border border-slate-800" alt="${p.name}">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-[10px] uppercase font-bold text-blue-400">${stockText}</span>
                            ${p.is_organic ? '<span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-bold">Organic</span>' : ''}
                        </div>
                        <h5 class="text-sm font-bold text-white line-clamp-1">${p.name}</h5>
                        <div class="text-base font-extrabold text-emerald-400 mt-1">${priceText}</div>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between gap-2 text-xs">
                        <a href="/buyer?product_id=${p.id}#product-${p.id}" target="_blank" class="text-amber-400 hover:underline flex items-center gap-1">
                            <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i> E-Mart
                        </a>
                        <button onclick="deleteSellerProduct(${p.id}, '${p.name.replace(/'/g, "\\'")}')" class="px-2.5 py-1 rounded-lg bg-rose-500/20 hover:bg-rose-500/40 text-rose-300 font-bold text-xs border border-rose-500/40 transition flex items-center gap-1 shadow-sm">
                            <i class="fa-solid fa-trash-can text-[11px]"></i> Delete
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            });

            const statInv = document.getElementById('statInventoryCount');
            if (statInv) statInv.innerText = `${json.products.length} Products`;
        }
    } catch (err) {
        console.error(err);
    }
}

async function deleteSellerProduct(productId, productName) {
    if (!confirm(`⚠️ Are you sure you want to delete "${productName}"?\n\nThis product will be permanently removed from your inventory, the database, and the Buyer E-Mart store.`)) {
        return;
    }

    try {
        const res = await fetch(`/api/products/${productId}`, {
            method: 'DELETE'
        });
        const json = await res.json();
        if (json.success) {
            showSellerToast(
                'Product Deleted',
                `<strong>${productName}</strong> has been removed from database and Buyer E-Mart.`,
                null
            );
            loadSellerInventory();
        } else {
            alert('⚠️ ' + (json.message || 'Error deleting product.'));
        }
    } catch (err) {
        console.error(err);
        alert('Server error while deleting product.');
    }
}

// ==============================================================================
// 4. BUYER ORDERS & DELIVERY FULFILLMENT
// ==============================================================================
async function loadSellerOrders() {
    const tbody = document.getElementById('sellerOrdersTableBody');
    if (!tbody) return;

    try {
        const sellerId = localStorage.getItem('user_id') || 2;
        const res = await fetch(`/api/seller/orders?seller_id=${sellerId}`);
        const json = await res.json();
        
        if (json.success) {
            tbody.innerHTML = '';
            if (json.orders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="p-6 text-center text-slate-500">No buyer orders received yet.</td></tr>';
                return;
            }

            json.orders.forEach(o => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/50 transition';
                tr.innerHTML = `
                    <td class="p-3.5 font-bold text-white">#${o.order_number}</td>
                    <td class="p-3.5">${o.buyer_name || 'Buyer Customer'}</td>
                    <td class="p-3.5 font-semibold text-white">${o.product_name} (${o.quantity} units)</td>
                    <td class="p-3.5 text-emerald-400 font-bold">₹${(Number(o.total_price) || 0).toFixed(2)}</td>
                    <td class="p-3.5">
                        <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${
                            o.order_status === 'delivered' ? 'bg-emerald-500/20 text-emerald-400' :
                            o.order_status === 'shipped' ? 'bg-blue-500/20 text-blue-400' : 'bg-amber-500/20 text-amber-400'
                        }">
                            ${o.order_status.replace('_', ' ').toUpperCase()}
                        </span>
                    </td>
                    <td class="p-3.5">
                        <select onchange="updateOrderStatus(${o.id}, this.value)" class="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white">
                            <option value="placed" ${o.order_status === 'placed' ? 'selected' : ''}>Placed</option>
                            <option value="processing" ${o.order_status === 'processing' ? 'selected' : ''}>Processing</option>
                            <option value="shipped" ${o.order_status === 'shipped' ? 'selected' : ''}>Shipped</option>
                            <option value="out_for_delivery" ${o.order_status === 'out_for_delivery' ? 'selected' : ''}>Out for Delivery</option>
                            <option value="delivered" ${o.order_status === 'delivered' ? 'selected' : ''}>Delivered</option>
                        </select>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

async function updateOrderStatus(orderId, status) {
    try {
        const res = await fetch(`/api/seller/orders/${orderId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        const json = await res.json();
        if (json.success) {
            alert('Order fulfillment status updated!');
            loadSellerOrders();
        }
    } catch (err) {
        console.error(err);
    }
}


// ==============================================================================
// 4. ANALYTICS CHARTS (Chart.js)
// ==============================================================================
function initSellerCharts() {
    const sourcingCtx = document.getElementById('sourcingChart');
    if (sourcingCtx) {
        new Chart(sourcingCtx, {
            type: 'bar',
            data: {
                labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep (Current)'],
                datasets: [{
                    label: 'Sourced Harvest (Quintals)',
                    data: [120, 190, 240, 310, 480],
                    backgroundColor: '#3b82f6',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });
    }

    const catCtx = document.getElementById('categoryChart');
    if (catCtx) {
        new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: ['Fresh Farm Produce', 'Organic Fertilizers', 'Chemical Fungicides', 'Hybrid Seeds'],
                datasets: [{
                    data: [82500, 31000, 24700, 16000],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#94a3b8' } } }
            }
        });
    }
}

