$(document).ready(function () {
    // Adiciona um ícone de carregamento
    const loadingIcon = `<span class="loading-icon">🕒</span>`;

    // Função para mostrar o ícone de carregamento no campo de CEP
    function showLoadingIcon() {
        $('input[name="cep"]').after(loadingIcon);
    }

    // Função para remover o ícone de carregamento do campo de CEP
    function hideLoadingIcon() {
        $('.loading-icon').remove();
    }

    // Função para limitar o texto conforme o maxlength do input
    function truncateToMaxLength(inputName, value) {
        const maxLength = $(`input[name="${inputName}"]`).attr('maxlength');
        if (maxLength && value.length > maxLength) {
            return value.substring(0, maxLength); // Corta o valor até o maxlength
        }
        return value; // Retorna o valor se não ultrapassar o limite
    }

    // Quando o CEP é alterado
    $('input[name="cep"]').on('blur', function () {
        const cep = $(this).val().replace(/\D/g, ''); // Remove caracteres não numéricos

        if (cep.length === 8) { // Verifica se o CEP tem 8 dígitos
            // Mostrar indicador de carregamento no campo de CEP
            showLoadingIcon();

            $.ajax({
                url: `https://viacep.com.br/ws/${cep}/json/`,
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    if (data.erro) {
                        alert('CEP não encontrado.');
                    } else {
                        // Remove indicador de carregamento do campo de CEP
                        hideLoadingIcon();

                        // Preenche os campos com os dados recebidos, cortando o valor conforme o maxlength de cada campo
                        $('input[name="ibge"]').val(truncateToMaxLength('ibge', data.ibge)).prop('readonly', false);
                        $('input[name="bairro"]').val(truncateToMaxLength('bairro', data.bairro)).prop('readonly', false);
                        $('input[name="rua"]').val(truncateToMaxLength('rua', data.logradouro)).prop('readonly', false);
                        $('input[name="cidade"]').val(truncateToMaxLength('cidade', data.localidade)).prop('readonly', false);
                        $('input[name="estado"]').val(truncateToMaxLength('estado', data.uf)).prop('readonly', false);
                        $('input[name="numero"]').val('').prop('readonly', false); // Permite ao usuário adicionar o número
                    }
                },
                error: function () {
                    hideLoadingIcon();
                    alert('Erro ao buscar dados do CEP.');
                }
            });
        }
    });
});
