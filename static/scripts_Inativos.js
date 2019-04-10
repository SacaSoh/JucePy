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
    var table = $('#inativos').DataTable( {
        "ajax": {
        "url": "/inativos",
        "type": "POST"
                },
        scrollY:        true,
        scrollX:        true,
        scrollCollapse: true,
        paging:         true,
		columnDefs: [
            { width: 275, targets: 8 }
        ],
        "columns": [
            {
                "className":      'details-control',
                "orderable":      false,
                "data":           null,
                "defaultContent": ''
            },
            { "data": "timestamp" },
            { "data": "protocol" },
            { "data": "uf" },
            { "data": "nomeemp" },
            { "data": "descricao" },
            { "data": "status" },
            { "data": "dataaprovacao" },
            { "data": "msgjucec" },
            { "data": "nire" },
            { "data": "cnpj" },
            { "data": "respadd" },
            { "data": "respbaixa" },
            { "data": "dataentrada" }
        ],
        "order": [[1, 'desc']]
    } );


// Add event listener for opening and closing details
$('#inativos tbody').on('click', 'td.details-control', function () {
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