// Extracted script from templates/index.html
const PRICES  = {1:159, 2:259, 3:329, 4:399};
const SIZES   = ['M','L','XL','XXL'];
const COLORS  = window.APP?.COLORS || ['أحمر'];
const ORDER_ITEM_LABEL = window.APP?.ORDER_ITEM_LABEL || 'قميص';
const MSG_INVALID_ORDER = window.APP?.MSG_INVALID_ORDER || 'يرجى ملء جميع الحقول المطلوبة بشكل صحيح.';
const WA_NUM  = window.APP?.WA_NUM || '';

let currentQty   = 1;
let selectedSize = 'L';

function switchImg(el) {
  document.getElementById('mainImg').src = el.src;
  document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
}

function selectPricing(qty, price, el) {
  document.querySelectorAll('.pricing-card').forEach(c => c.classList.remove('selected'));
  if (el && el.currentTarget) el.currentTarget.classList.add('selected');
  setQty(qty);
  document.getElementById('order').scrollIntoView({behavior:'smooth'});
}

function selectSize(size, el) {
  selectedSize = size;
  document.querySelectorAll('.size-card').forEach(c => c.classList.remove('active'));
  if (el) el.classList.add('active');
  const firstSize = document.querySelector('.item-size');
  if (firstSize) firstSize.value = size;
}

function pickQty(el) {
  document.querySelectorAll('.qty-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  currentQty = parseInt(el.dataset.qty);
  updateTotal();
  renderOrderItems();
}

function setQty(n) {
  const btn = document.querySelector(`.qty-btn[data-qty="${n}"]`);
  if (btn) pickQty(btn);
}

function renderOrderItems() {
  const container = document.getElementById('orderItems');
  container.innerHTML = '';
  for (let i = 1; i <= currentQty; i++) {
    container.innerHTML += `
      <div class="order-item">
        <div class="item-num">${i}</div>
        <select class="item-color">
          ${COLORS.map(c => `<option>${c}</option>`).join('')}
        </select>
        <select class="item-size">
          ${SIZES.map(s => `<option value="${s}" ${s===selectedSize?'selected':''}>${s}</option>`).join('')}
        </select>
        <span style="font-size:0.75rem;color:var(--muted);text-align:center">${ORDER_ITEM_LABEL} ${i}</span>
      </div>`;
  }
}

function updateTotal() {
  const price = PRICES[currentQty] || 159;
  document.getElementById('totalAmount').textContent = price + ' DH';
}

function validateField(id, check) {
  const field = document.getElementById('field-' + id);
  const val   = document.getElementById('c' + id.charAt(0).toUpperCase() + id.slice(1)).value.trim();
  const ok    = check(val);
  if (field) field.classList.toggle('has-error', !ok);
  return ok;
}

function validateAll() {
  const nameOk  = validateField('name',  v => v.length >= 2);
  const phoneOk = validateField('phone', v => /^[0-9\+\s\-]{9,15}$/.test(v));
  const cityOk  = validateField('city',  v => v.length >= 2);
  return nameOk && phoneOk && cityOk;
}

function submitOrder() {
  if (!validateAll()) {
    showMsg('error', MSG_INVALID_ORDER);
    return;
  }

  const name  = document.getElementById('cName').value.trim();
  const phone = document.getElementById('cPhone').value.trim();
  const city  = document.getElementById('cCity').value.trim();
  const addr  = document.getElementById('cAddr').value.trim();
  const price = PRICES[currentQty];

  const items = [...document.querySelectorAll('.order-item')].map((row, i) => {
    const color = row.querySelector('.item-color').value;
    const size  = row.querySelector('.item-size').value;
    return `  قميص ${i+1}: ${color} / ${size}`;
  }).join('\n');

  const msg = [
    `🛒 *طلب جديد — M&A Elite Kits*`,
    ``,
    `👤 الاسم: ${name}`,
    `📞 الهاتف: ${phone}`,
    `📍 المدينة: ${city}`,
    addr ? `🏠 العنوان: ${addr}` : '',
    ``,
    `*تفاصيل الطلب:*`,
    items,
    ``,
    `💰 المجموع: ${price} DH`,
    `✅ الدفع عند الاستلام`,
  ].filter(Boolean).join('\n');

  const url = `https://wa.me/${WA_NUM}?text=${encodeURIComponent(msg)}`;
  window.open(url, '_blank');
  showMsg('success');
}

function showMsg(type, text) {
  document.getElementById('msgSuccess').style.display = 'none';
  document.getElementById('msgError').style.display   = 'none';
  if (type === 'success') {
    document.getElementById('msgSuccess').style.display = 'block';
  } else {
    if (text) document.getElementById('msgErrorText').textContent = text;
    document.getElementById('msgError').style.display = 'block';
  }
}

function togglePolicy(id) {
  const item = document.getElementById(id);
  const isOpen = item.classList.contains('open');
  document.querySelectorAll('.policy-item.open').forEach(i => i.classList.remove('open'));
  if (!isOpen) item.classList.add('open');
}

document.addEventListener('DOMContentLoaded', () => {
  renderOrderItems();
  updateTotal();
  ['cName','cPhone','cCity'].forEach(id => {
    document.getElementById(id)?.addEventListener('blur', validateAll);
  });
});
