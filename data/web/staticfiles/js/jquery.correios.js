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
                        
                        // Preenche os campos com os dados recebidos
                        $('input[name="ibge"]').val(data.ibge).prop('readonly', false);
                        $('input[name="bairro"]').val(data.bairro).prop('readonly', true);
                        $('input[name="rua"]').val(data.logradouro).prop('readonly', true);
                        $('input[name="cidade"]').val(data.localidade).prop('readonly', true);
                        $('input[name="estado"]').val(data.uf).prop('readonly', true);
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