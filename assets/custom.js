document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('btn-download');
  if (btn) {
    btn.addEventListener('click', function () {
      btn.innerText = "Генерируем файл...";
      setTimeout(() => {
        btn.innerText = "Скачать CSV";
      }, 2000);
    });
  }
});