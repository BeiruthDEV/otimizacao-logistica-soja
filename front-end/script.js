/**
 * Controla a navegação por abas no painel principal.
 * @param {string} viewId O ID do elemento de conteúdo a ser exibido.
 * @param {HTMLElement} clickedButton O botão que foi clicado.
 */
function showView(viewId, clickedButton) {
    // 1. Esconde todas as "views" (abas de conteúdo)
    document.querySelectorAll('.view-content').forEach(view => {
        view.style.display = 'none';
    });

    // 2. Remove a classe 'active' de todos os botões do menu
    document.querySelectorAll('.menu-item').forEach(button => {
        button.classList.remove('active');
    });

    // 3. Mostra a view clicada
    const viewToShow = document.getElementById(viewId);
    if (viewToShow) {
        viewToShow.style.display = 'block';
    }

    // 4. Adiciona a classe 'active' apenas ao botão clicado
    if (clickedButton) {
        clickedButton.classList.add('active');
    }
}

// Opcional: Garante que a view padrão esteja correta no carregamento
// (Embora o CSS já faça isso, é uma boa prática)
document.addEventListener('DOMContentLoaded', () => {
    // Verifica se a view-0 existe antes de tentar mostrá-la
    if (document.getElementById('view-0')) {
        document.getElementById('view-0').style.display = 'block';
    }

    // Encontra o primeiro botão (Sobre o Projeto) e o marca como ativo
    const firstButton = document.querySelector('.menu-item');
    if (firstButton) {
        firstButton.classList.add('active');
    }
});