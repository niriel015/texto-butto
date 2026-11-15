(() => {
  'use strict';
  const menuButton = document.querySelector('[data-menu-toggle]');
  const menu = document.getElementById('mobile-nav');
  if (menuButton && menu) {
    menuButton.addEventListener('click', () => {
      const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
      menu.hidden = isOpen;
      menuButton.setAttribute('aria-expanded', String(!isOpen));
      menuButton.setAttribute('aria-label', isOpen ? 'Abrir menu' : 'Fechar menu');
    });
    menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      menu.hidden = true;
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'Abrir menu');
    }));
  }
  document.querySelectorAll('[data-dismiss]').forEach(button => {
    button.addEventListener('click', () => button.closest('.flash')?.remove());
  });
  document.querySelectorAll('[data-auto-submit]').forEach(select => {
    select.addEventListener('change', () => select.form?.requestSubmit());
  });
  document.querySelectorAll('[data-quantity-step]').forEach(button => {
    button.addEventListener('click', () => {
      const input = button.closest('form')?.querySelector('input[name="quantity"]');
      if (!input) return;
      const minimum = Number(input.min || 0), maximum = Number(input.max || 99);
      const next = Math.max(minimum, Math.min(maximum, (Number(input.value) || 0) + Number(button.dataset.quantityStep)));
      input.value = String(next);
      input.form?.requestSubmit();
    });
  });
  document.querySelectorAll('[data-copy-pix]').forEach(button => {
    button.addEventListener('click', async () => {
      const field = document.getElementById(button.dataset.copyPix);
      const feedback = document.querySelector('[data-copy-feedback]');
      if (!field) return;
      try {
        await navigator.clipboard.writeText(field.value);
        if (feedback) feedback.textContent = 'Código Pix copiado com sucesso.';
      } catch {
        if (feedback) feedback.textContent = 'Não foi possível copiar automaticamente. Selecione e copie o código acima.';
        field.focus(); field.select();
      }
    });
  });
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const targets = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {entry.target.classList.add('in-view'); observer.unobserve(entry.target);}
      });
    }, {threshold: 0.07, rootMargin: '0px 0px -25px 0px'});
    targets.forEach(item => observer.observe(item));
  } else {targets.forEach(item => item.classList.add('in-view'));}

  // Motion effects only on fine-pointer devices, never interfere with forms or links.
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  if (finePointer.matches && !reducedMotion.matches) {
    const heroArt = document.querySelector('.hero-art');
    if (heroArt) {
      heroArt.addEventListener('pointermove', e => {
        const r = heroArt.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5;
        const y = (e.clientY - r.top) / r.height - .5;
        heroArt.style.setProperty('--hero-tilt-x', `${(x * 5).toFixed(2)}deg`);
        heroArt.style.setProperty('--hero-tilt-y', `${(-y * 5).toFixed(2)}deg`);
      }, {passive: true});
      heroArt.addEventListener('pointerleave', () => {
        heroArt.style.setProperty('--hero-tilt-x', '0deg');
        heroArt.style.setProperty('--hero-tilt-y', '0deg');
      });
    }
    const studio = document.querySelector('[data-tilt-stage]');
    if (studio) {
      studio.addEventListener('pointermove', e => {
        const r = studio.getBoundingClientRect();
        studio.style.setProperty('--studio-tilt-x', `${(((e.clientX - r.left) / r.width - .5) * 9).toFixed(2)}deg`);
        studio.style.setProperty('--studio-tilt-y', `${(-((e.clientY - r.top) / r.height - .5) * 9).toFixed(2)}deg`);
      }, {passive: true});
      studio.addEventListener('pointerleave', () => {
        studio.style.setProperty('--studio-tilt-x', '0deg');
        studio.style.setProperty('--studio-tilt-y', '0deg');
      });
    }
    document.querySelectorAll('.product-visual').forEach(card => {
      card.addEventListener('pointermove', e => {
        const r = card.getBoundingClientRect();
        card.style.setProperty('--glow-x', `${(e.clientX - r.left) / r.width * 100}%`);
        card.style.setProperty('--glow-y', `${(e.clientY - r.top) / r.height * 100}%`);
      }, {passive: true});
    });
  }

  // Document progress indicator and frosted header; throttled to animation frame.
  const progress = document.getElementById('reading-progress');
  const header = document.querySelector('.site-header');
  let pending = false;
  const paintScroll = () => {
    const scrollable = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    if (progress) progress.style.width = `${scrollable ? Math.min(100, window.scrollY / scrollable * 100) : 0}%`;
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 24);
    pending = false;
  };
  window.addEventListener('scroll', () => {
    if (!pending) {pending = true; requestAnimationFrame(paintScroll);}
  }, {passive: true});
  window.addEventListener('resize', () => {if (!pending) {pending = true; requestAnimationFrame(paintScroll);}}, {passive: true});
  paintScroll();
})();

// Carrossel de anúncios reais publicados pelo painel. Não inventa imagens/produtos.
(() => {
 const carousel=document.querySelector('[data-drica-carousel]');
 if(!carousel)return;
 const slides=[...carousel.querySelectorAll('[data-drica-slide]')];
 const dots=[...carousel.querySelectorAll('[data-drica-dot]')];
 if(slides.length < 2)return;
 let current=0, timer;
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 function show(index){
  current=(index+slides.length)%slides.length;
  slides.forEach((s,i)=>{
   const active=i===current;
   s.classList.toggle('is-active',active);
   s.setAttribute('aria-hidden',String(!active));
   s.querySelectorAll('a,button').forEach(el=>{if(active)el.removeAttribute('tabindex');else el.setAttribute('tabindex','-1')});
  });
  dots.forEach((d,i)=>{d.classList.toggle('is-active',i===current);d.setAttribute('aria-current',i===current?'true':'false')});
 }
 function stop(){if(timer)window.clearInterval(timer)}
 function begin(){stop();if(!reduced)timer=window.setInterval(()=>show(current+1),6500)}
 carousel.querySelector('[data-drica-prev]')?.addEventListener('click',()=>{show(current-1);begin()});
 carousel.querySelector('[data-drica-next]')?.addEventListener('click',()=>{show(current+1);begin()});
 dots.forEach((d,i)=>d.addEventListener('click',()=>{show(i);begin()}));
 carousel.addEventListener('mouseenter',stop);
 carousel.addEventListener('mouseleave',begin);
 carousel.addEventListener('focusin',stop);
 carousel.addEventListener('focusout',e=>{if(!carousel.contains(e.relatedTarget))begin()});
 document.addEventListener('visibilitychange',()=>document.hidden?stop():begin());
 show(0);begin();
})();
