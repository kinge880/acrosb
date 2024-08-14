

// Ocultar a tabela até que o carregamento esteja completo
$(document).ready(function() {
    var table = $('#myTable').DataTable({
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.10.24/i18n/Portuguese-Brasil.json"
        },
        //opção colReorder para permitir redimensionar e reordenar colunas
        colReorder: true,
        dom: "<'row'<'col-sm-12 col-md-3'l><'col-12 col-md-6'<'d-flex justify-content-center'B>><'col-sm-12 col-md-3 text-right'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        buttons: [
            {
                extend: 'copy',
                className: 'btn btn-primary',
                text: 'Copiar',
                title: '{{nometabela}}'
            },
            {
                extend: 'csv',
                className: 'btn btn-primary',
                text: 'CSV',
                title: '{{nometabela}}'
            },
            {
                extend: 'excel',
                className: 'btn btn-primary',
                text: 'Excel',
                title: '{{nometabela}}',
                autoFilter: true,
            },
            {
                extend: 'pdf',
                className: 'btn btn-primary',
                text: 'PDF',
                download: 'open',
                pageSize: 'LEGAL',
                orientation: 'landscape',
                title: '{{nometabela}}',

                split: [{
                    extend: 'pdf',
                    className: 'btn btn-primary',
                    text: 'PDF VERTICAL',
                    download: 'open',
                    pageSize: 'LEGAL',
                    title: '{{nometabela}}'
                }],
            },
            {
                extend: 'print',
                className: 'btn btn-primary',
                text: 'Imprimir',
                title: '{{nometabela}}'
            },
            {
                extend: 'colvis',
                className: 'btn btn-primary',
                text: 'Esconder colunas',
                collectionLayout: 'fixed columns',
                collectionTitle: 'Definir visibilidade das colunas'
            }
        ],
        lengthMenu: [[10, 15, 25, 50, 100, -1], [10, 15, 25, 50, 100, "Tudo"]],
        colReorder: true, 
        drawCallback: function(settings) {
            // Oculta a div 'loaddinamic' com animação de fadeOut
            $('.dtfc-left').removeClass('dtfc-left');
            $('#loaddinamic').fadeOut(400, function() {
                $(this).addClass("d-none").removeClass("d-flex");
                $('#dinamictable').addClass("d-flex").removeClass("d-none");

                // Exibe a div 'dinamictable' com animação de fadeIn
                $('#dinamictable').fadeTo(400, 1, function() {});
            });

            // Salve o estado das colunas em cookies após o redimensionamento ou reordenação
            var colState = table.colReorder.order();
            Cookies.set('colState', colState);
        }
    });

    // Adicionar a classe "btn-primary" aos botões
    $('.dt-buttons button').addClass('btn-primary');

    // Restaure o estado das colunas a partir dos cookies
    var colState = Cookies.getJSON('colState');
    if (colState) {
        table.colReorder.order(colState);
        table.draw();
    }

});