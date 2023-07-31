function adjustFooter() {
  const footer = document.getElementById('my-footer');
  const pageHeight = document.documentElement.scrollHeight;
  const windowHeight = window.innerHeight;
  if (pageHeight > windowHeight) {
    footer.classList.remove('fixed-bottom');
  } else {
    footer.classList.add('fixed-bottom');
  }
}

window.addEventListener('load', adjustFooter);
window.addEventListener('resize', adjustFooter);