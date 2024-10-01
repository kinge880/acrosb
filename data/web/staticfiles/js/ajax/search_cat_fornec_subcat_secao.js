$(document).ready(function() {
    var secaoValue = "{{secao}}";
    console.log(secaoValue)

    $('.marca').select2({
      language: 'pt-BR',
      placeholder: 'Selecione uma marca', // Placeholder desejado
      ajax: {
          url: '/reusable/utils/pesquisarmarca/', // URL da sua view Django que faz a pesquisa no banco de dados
          dataType: 'json',
          delay: 250,
          processResults: function(data) {
              return {
                  results: data.data
              };
          },
          cache: true
      },
      minimumInputLength: 0,
      templateSelection: function(data) {
          if (data.id === '') {
              return 'Selecione uma marca';
          }
          var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
          var $selection = $('<span class="text-dark"> ' + data.text + '</span>');
          $removeIcon.on('click', function(e) {
              e.stopPropagation();
              $('.marca').val(null).trigger('change');
          });
          $selection.append($removeIcon);
          return $selection;
          }
      });
    
    $('#secao').select2({
    language: 'pt-BR',
    placeholder: 'Selecione uma seção', // Placeholder desejado
    ajax: {
        url: '/reusables/utils/pesquisarsecoes/', // URL da sua view Django que faz a pesquisa no banco de dados
        dataType: 'json',
        delay: 250,
        processResults: function(data) {
            return {
              results: data.data
            };
          },
          cache: true
      },
      minimumInputLength: 1,
      templateSelection: function(data) {
        if (data.id === '') {
            return 'Selecione uma seção';
        }
        var $selection = $('<span> ' + data.text + '</span>');
        var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
        $removeIcon.on('click', function(e) {
            e.stopPropagation();
            $('#secao').val(null).trigger('change');
        });
        $selection.append($removeIcon);
        return $selection;
        }
    });

    // Define o valor selecionado após a inicialização do Select2
    if (secaoValue > 0) {
        console.log('change')
        $('#secao').append(new Option(secaoValue, secaoValue, true, true));
        $('#secao').trigger('change');
    }

    $('#categoria').select2({
        language: 'pt-BR',
        placeholder: 'Selecione uma categoria', // Placeholder desejado
        ajax: {
            url: '/reusables/utils/pesquisarcategorias/', // URL da sua view Django que faz a pesquisa no banco de dados
            dataType: 'json',
            delay: 250, 
            data: function(params) {
                return {
                    secao_id: $('#secao').val(), // Captura o valor da seção selecionada
                    term: params.term // Captura o termo de pesquisa digitado
                };
            },
            processResults: function(data) {
                return {
                    results: data.data
                };
              },
              cache: true
          },
          minimumInputLength: 1,
          templateSelection: function(data) {
            if (data.id === '') {
                return 'Selecione uma categoria';
            }
            var $selection = $('<span> ' + data.text + '</span>');
            var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
            $removeIcon.on('click', function(e) {
                e.stopPropagation();
                $('#categoria').val(null).trigger('change');
            });
            $selection.append($removeIcon);
            return $selection;
        }
     });

     $('#subcat').select2({
        language: 'pt-BR',
        placeholder: 'Selecione uma subcategoria', // Placeholder desejado
        ajax: {
            url: '/reusables/utils/pesquisasubcat/', // URL da sua view Django que faz a pesquisa no banco de dados
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    categoria_id: $('#categoria').val(), // Captura o valor da categoria selecionada
                    term: params.term // Captura o termo de pesquisa digitado
                };
            },
            processResults: function(data) {
                return {
                  results: data.data
                };
              },
              cache: true
          },
          minimumInputLength: 1,
          templateSelection: function(data) {
            if (data.id === '') {
                return 'Selecione uma subcategoria';
            }
            var $selection = $('<span> ' + data.text + '</span>');
            var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
            $removeIcon.on('click', function(e) {
                e.stopPropagation();
                $('#subcat').val(null).trigger('change');
            });
            $selection.append($removeIcon);
            return $selection;
        }
     });

     $('#codfornec').select2({
        language: 'pt-BR',
        placeholder: 'Selecione um fornecedor', // Placeholder desejado
        ajax: {
            url: '/reusables/utils/pesquisafornec/', // URL da sua view Django que faz a pesquisa no banco de dados
            dataType: 'json',
            delay: 250,
            processResults: function(data) {
                return {
                  results: data.data
                };
              },
              cache: true
          },
          minimumInputLength: 1,
          templateSelection: function(data) {
            if (data.id === '') {
                return 'Selecione um fornecedor';
            }
            var $selection = $('<span> ' + data.text + '</span>');
            var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
            $removeIcon.on('click', function(e) {
                e.stopPropagation();
                $('#codfornec').val(null).trigger('change');
            });
            $selection.append($removeIcon);
            return $selection;
            }
    });

    $('#produto').select2({
      language: 'pt-BR',
      placeholder: 'Selecione um produto', // Placeholder desejado
      ajax: {
          url: '/reusables/utils/pesquisarcodprod/', // URL da sua view Django que faz a pesquisa no banco de dados
          dataType: 'json',
          delay: 250,
          processResults: function(data) {
              return {
                results: data.data
              };
            },
            cache: true
        },
        minimumInputLength: 1,
        templateSelection: function(data) {
          if (data.id === '') {
              return 'Selecione um produto';
          }
          var $selection = $('<span> ' + data.text + '</span>');
          var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
          $removeIcon.on('click', function(e) {
              e.stopPropagation();
              $('#produto').val(null).trigger('change');
          });
          $selection.append($removeIcon);
          return $selection;
          }
    });

    $('#codprod').select2({
      language: 'pt-BR',
      placeholder: 'Selecione um produto', // Placeholder desejado
      ajax: {
          url: '/reusables/utils/pesquisarcodprod/pcprodut/', // URL da sua view Django que faz a pesquisa no banco de dados
          dataType: 'json',
          delay: 250,
          processResults: function(data) {
              return {
                results: data.data
              };
            },
            cache: true
        },
        minimumInputLength: 1,
        templateSelection: function(data) {
          if (data.id === '') {
              return 'Selecione um produto';
          }
          var $selection = $('<span> ' + data.text + '</span>');
          var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
          $removeIcon.on('click', function(e) {
              e.stopPropagation();
              $('#codprod').val(null).trigger('change');
          });
          $selection.append($removeIcon);
          return $selection;
          }
    });

    $('#embalagem').select2({
      language: 'pt-BR',
      placeholder: 'Selecione um produto', // Placeholder desejado
      ajax: {
          url: '/reusables/utils/pesquisarembalagem/', // URL da sua view Django que faz a pesquisa no banco de dados
          dataType: 'json',
          delay: 250,
          processResults: function(data) {
              return {
                results: data.data
              };
            },
            cache: true
        },
        minimumInputLength: 1,
        templateSelection: function(data) {
          if (data.id === '') {
              return 'Selecione uma embalagem';
          }
          var $selection = $('<span> ' + data.text + '</span>');
          var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
          $removeIcon.on('click', function(e) {
              e.stopPropagation();
              $('#embalagem').val(null).trigger('change');
          });
          $selection.append($removeIcon);
          return $selection;
          }
    });

    $('#descricao').select2({
      language: 'pt-BR',
      placeholder: 'Escreva a descrição do produto', // Placeholder desejado
      ajax: {
          url: '/reusables/utils/pesquisadescricao/', // URL da sua view Django que faz a pesquisa no banco de dados
          dataType: 'json',
          delay: 950,
          processResults: function(data) {
              return {
                results: data.data
              };
            },
            cache: true
        },
        minimumInputLength: 1,
        templateSelection: function(data) {
          if (data.id === '') {
              return 'Escreva a descrição do produto';
          }
          var $selection = $('<span> ' + data.text + '</span>');
          var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
          $removeIcon.on('click', function(e) {
              e.stopPropagation();
              $('#descricao').val(null).trigger('change');
          });
          $selection.append($removeIcon);
          return $selection;
          }
    });

    $('#departamento').select2({
      language: 'pt-BR',
      placeholder: 'Selecione um departamento', // Placeholder desejado
      ajax: {
          url: '/reusables/utils/pesquisardepartamento/', // URL da sua view Django que faz a pesquisa no banco de dados
          dataType: 'json',
          delay: 250,
          processResults: function(data) {
              return {
                results: data.data
              };
            },
            cache: true
        },
        minimumInputLength: 1,
        templateSelection: function(data) {
          if (data.id === '') {
              return 'Selecione um departamento';
          }
          var $selection = $('<span> ' + data.text + '</span>');
          var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
          $removeIcon.on('click', function(e) {
              e.stopPropagation();
              $('#departamento').val(null).trigger('change');
          });
          $selection.append($removeIcon);
          return $selection;
          }
    });

    $('#codconta').select2({
      language: 'pt-BR',
      placeholder: 'Selecione uma conta', // Placeholder desejado
      ajax: {
          url: '/reusables/utils/pesquisaconta/', // URL da sua view Django que faz a pesquisa no banco de dados
          dataType: 'json',
          delay: 250,
          processResults: function(data) {
              return {
                results: data.data
              };
            },
            cache: true
        },
        minimumInputLength: 1,
        templateSelection: function(data) {
          if (data.id === '') {
              return 'Selecione uma conta';
          }
          var $selection = $('<span> ' + data.text + '</span>');
          var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
          $removeIcon.on('click', function(e) {
              e.stopPropagation();
              $('#codconta').val(null).trigger('change');
          });
          $selection.append($removeIcon);
          return $selection;
          }
  });

  $('#codcontagrupo').select2({
    language: 'pt-BR',
    placeholder: 'Selecione uma conta', // Placeholder desejado
    ajax: {
        url: '/reusables/utils/pesquisacontagrupo/', // URL da sua view Django que faz a pesquisa no banco de dados
        dataType: 'json',
        delay: 250,
        processResults: function(data) {
            return {
              results: data.data
            };
          },
          cache: true
      },
      minimumInputLength: 1,
      templateSelection: function(data) {
        if (data.id === '') {
            return 'Selecione uma conta';
        }
        var $selection = $('<span> ' + data.text + '</span>');
        var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
        $removeIcon.on('click', function(e) {
            e.stopPropagation();
            $('#codcontagrupo').val(null).trigger('change');
        });
        $selection.append($removeIcon);
        return $selection;
        }
});


    $('#numagendamento').select2({
        language: 'pt-BR',
        placeholder: 'Selecione um fornecedor', // Placeholder desejado
        ajax: {
            url: '/reusables/utils/pesquisaAgendamentos/', // URL da sua view Django que faz a pesquisa no banco de dados
            dataType: 'json',
            delay: 250,
            processResults: function(data) {
                return {
                  results: data.data
                };
              },
              cache: true
          },
          minimumInputLength: 1,
          templateSelection: function(data) {
            if (data.id === '') {
                return 'Selecione um numero de pedido';
            }
            var $selection = $('<span> ' + data.text + '</span>');
            var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
            $removeIcon.on('click', function(e) {
                e.stopPropagation();
                $('#numagendamento').val(null).trigger('change');
            });
            $selection.append($removeIcon);
            return $selection;
            }
    });


    
    $('#codfornecinput').select2({
        language: 'pt-BR',
        placeholder: 'Selecione um fornecedor', // Placeholder desejado
        ajax: {
            url: '/reusables/utils/pesquisafornec/', // URL da sua view Django que faz a pesquisa no banco de dados
            dataType: 'json',
            delay: 250,
            processResults: function(data) {
                return {
                  results: data.data
                };
              },
              cache: true
          },
          minimumInputLength: 1,
          templateSelection: function(data) {
            if (data.id === '') {
                return 'Selecione um fornecedor';
            }
            var $selection = $('<span> ' + data.text + '</span>');
            var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
            $removeIcon.on('click', function(e) {
                e.stopPropagation();
                $('#codfornec').val(null).trigger('change');
            });
            $selection.append($removeIcon);
            return $selection;
            }
    });
    
    $(document).ready(function() {
        // Inicializa o Select2 com pesquisa em tempo real
        $('#codfornecinput').select2({
          minimumInputLength: 1, // Define o número mínimo de caracteres para iniciar a busca
          ajax: {
            url: "/reusables/utils/pesquisafornec/", // URL para a requisição AJAX que retornará as opções
            dataType: 'json',
            delay: 250,
            data: function(params) {
              return {
                term: params.term // Envia o valor digitado como o parâmetro term
              };
            },
            processResults: function(data) {
              return {
                results: data.data
              };
            },
            cache: true
          }
        });
      });

      $('#codfornecinput').select2({
        dropdownParent: $('#inserir'),
        language: 'pt-BR',
        placeholder: 'Selecione um fornecedor', // Placeholder desejado
        ajax: {
            url: '/reusables/utils/pesquisaAgendamentos/', // URL da sua view Django que faz a pesquisa no banco de dados
            dataType: 'json',
            delay: 250,
            processResults: function(data) {
                return {
                  results: data.data
                };
              },
              cache: true
          },
          minimumInputLength: 1,
          templateSelection: function(data) {
            if (data.id === '') {
                return 'Selecione um numero de pedido';
            }
            var $selection = $('<span> ' + data.text + '</span>');
            var $removeIcon = $('<button type="button" class="remove-icon close" aria-label="Close"><span aria-hidden="true">&times;</span></button>');
            $removeIcon.on('click', function(e) {
                e.stopPropagation();
                $('#numagendamento').val(null).trigger('change');
            });
            $selection.append($removeIcon);
            return $selection;
            }
      });


  });