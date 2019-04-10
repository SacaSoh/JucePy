/* datatables! - https://datatables.net/examples/api/row_details.html */
/* Formatting function for row details - modify as you need */

function format ( rowData ) {
    var div = $('<div/ class=slider>')
        .addClass( 'loading' )
        .text( 'Carregando Informações...' );

    $.ajax( {
        url: '/historico',
        type: "POST",
        data:  JSON.stringify({ 'data': rowData.protocol }),
        dataType: "json",
        contentType: "application/json",
        success: function ( json ) {

            div
            .removeClass( 'loading' )
            console.log( 'Retrieved JSON Length:' + json.length );
            if(json.length === 0){ return "<tr>Sem histórico para o processo</tr>"};

            // if there's process history, prepare a "sub table" to be appended to the html
            var historico = ('<header>' +
                            '<div class="border histheader" style="width:60%">' +
                                '<h5>Histórico do Processo</h5>' +
                              '</div>' +
                            '</header>' +
                            '<table id="subtable" class="display table-striped historico" style="width:60%">' +
                                '<thead>' +
                                    '<tr>' +
                                        '<th>#</th>' +
                                        '<th>Data do Evento</th>' +
                                        '<th>Situação</th>' +
                                        '<th>Notas</th>' +
                                        '<th>Data de Retorno</th>' +
                                    '</tr>' +
                                '</thead>' +
                                '<tbody>');

            var i;
            for (i = 0; i < json.length; i++) {

                historico +=  ('<td><b>'+parseInt(json.length - i)+'<b></td>'+
                              '<td class="dontwrap">'+json[i].dataevento+'</td>' +
                              '<td>'+json[i].status+'</td>' +
                              '<td>'+json[i].msgjucec+'</td>' +
                              '<td class="dontwrap">'+json[i].dataretorno+'</td>') +
                              '</tr>';
                }

            historico += ('</tbody>' + '</table>');

            div
            .html(historico)

            console.log('div ops')

        },
        error: function () {
            window.alert('ajax retrieve info error')
        }
    } );

    return div;
}

/* Table for active processes */
$(document).ready(function() {
    var table = $('#example').DataTable( {
        "ajax": {
        "url": "/",
        "type": "POST"
                },
        scrollY:        true,
        scrollX:        true,
        scrollCollapse: true,
        paging:         true,
		columnDefs: [
            { width: 260, targets: 8 }
        ],
        "columns": [
            {
                "className":      'details-control',
                "orderable":      false,
                "data":           null,
                "defaultContent": ''
            },
            { "data": "timestamp"},
            { "data": "protocol",
                    render: function ( data, type, row ) {
                    return row.protocol + '<br>(' + row.uf + ')';
                    }
            },
            { "data": "nomeemp" },
            { "data": "descricao" },
            { "data": "status" },
            { "data": "dataaprovacao" },
            { "data": "msgjucec" },
            { "data": "cnpj",
                    render: function ( data, type, row ) {
                    return row.cnpj + '<br>' + row.nire + '';
                    }
            },
            { "data": "respadd",
                    render: function ( data, type, row ) {
                    return row.respadd + '<br>(' + row.dataentrada + ')';
                    }
            },
            {  "className":      'finalizarprocesso',
                "orderable":      false,
                "data":           null,
                "defaultContent": "<button>Finalizar</button>"
            }
        ],
        "order": [[1, 'desc']]
    } );


// Button event for closing process, updating DB, and refreshing page
$('#example tbody').on( 'click', 'button', function () {
    var data = table.row( $(this).parents('tr') ).data();
    var row = table.row( $(this).parents('tr') );
            $.ajax({
            url: '/finalizar',
            type: "POST",
            data:  JSON.stringify({ 'data': data.protocol }),
            contentType: "application/json",
            success: function () {
                    alert('Processo nº ' + data.protocol + ' - ' + data.nomeemp + ' - ' + ' foi encerrado!');
                        row.remove();
                        table
                        .draw();
            },
            error: function () {
            window.alert('ajax send button data error');
            }
            })
});


// Add event listener for opening and closing details
$('#example tbody').on('click', 'td.details-control', function () {
    var tr = $(this).closest('tr');
    var row = table.row( tr );
    if ( row.child.isShown() ) {
                // This row is already open - close it
                $('div.slider', row.child()).slideUp( function () {
                    row.child.hide();
                    tr.removeClass('shown');
                } );
            }
            else {
                // Open this row
                row.child( format(row.data()), 'no-padding' ).show();
                tr.addClass('shown');

                $('div.slider', row.child()).slideDown();
            }
        } );
} );