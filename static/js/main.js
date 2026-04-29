document.addEventListener("DOMContentLoaded", () => {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        if (['cpf', 'cnpj', 'numero'].includes(input.name)) {
            input.setAttribute('type', 'text');
        }

        input.addEventListener('input', (e) => {
            let v = e.target.value.replace(/\D/g, '');

            if (e.target.name === 'cpf') {
                if (v.length <= 11) {
                    v = v.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
                } else {
                    v = v.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
                }
                e.target.value = v.substring(0, 18);
            }
            else if (e.target.name === 'cnpj') {
                v = v.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
                e.target.value = v.substring(0, 18);
            }
            else if (e.target.name === 'numero') { 
                v = v.replace(/^(\d{2})(\d)/g, "($1) $2");
                v = v.replace(/(\d{5})(\d{4})$/, "$1-$2");
                e.target.value = v.substring(0, 15);
            }
        });
    });

    const tipoConta = document.querySelector("#tipo-conta");
    if (tipoConta) {
        tipoConta.addEventListener("change", (e) => {
            const tipo = e.target.value;
            const comum = document.querySelector("#campos-comum");
            const equipe = document.querySelector("#campos-equipe");
            const org = document.querySelector("#campos-organizacao");
            const btn = document.querySelector("#btn-cadastrar");

            if(comum) comum.style.display = tipo === "usuario" ? "block" : "none";
            if(equipe) equipe.style.display = tipo === "equipe" ? "block" : "none";
            if(org) org.style.display = tipo === "organizacao" ? "block" : "none";
            if(btn) btn.style.display = tipo ? "block" : "none";
        });
    }

    if (window.location.pathname.includes('/login') || document.querySelector('input[placeholder="CPF/CNPJ"]')) {
        const formLogin = document.querySelector("form");
        if (formLogin) {
            formLogin.addEventListener("submit", (e) => {
                const cpf = formLogin.querySelector("input[name='cpf']").value;
                const senha = formLogin.querySelector("input[name='password']").value;
                if (!cpf || !senha) {
                    e.preventDefault();
                    showToast("Preencha CPF/CNPJ e a senha.", "error");
                } else {
                    showToast("Conectando...", "success");
                }
            });
        }
    }
});

function showToast(msg, tipo) {
    const t = document.createElement("div");
    t.innerText = msg;
    const cor = tipo === 'error' ? '#d9534f' : '#5cb85c';
    t.style.cssText = `position:fixed; bottom:20px; right:20px; background:${cor}; color:#fff; padding:15px; border-radius:8px; z-index:1000; font-family:sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.1);`;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}
