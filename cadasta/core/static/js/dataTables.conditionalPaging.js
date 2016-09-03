/**
 * @summary     ConditionalPaging
 * @description Hide paging controls when the amount of pages is <= 1
 * @version     1.0.0
 * @file        dataTables.conditionalPaging.js
 * @author      Matthew Hasbach (https://github.com/mjhasbach)
 * @contact     hasbach.git@gmail.com
 * @copyright   Copyright 2015 Matthew Hasbach
 *
 * License      MIT - http://datatables.net/license/mit
 *
 * This feature plugin for DataTables hides paging controls when the amount
 * of pages is <= 1. The controls can either appear / disappear or fade in / out
 *
 * @example
 *    $('#myTable').DataTable({
 *        conditionalPaging: true
 *    });
 *
 * @example
 *    $('#myTable').DataTable({
 *        conditionalPaging: {
 *            style: 'fade',
 *            speed: 500 // optional
 *        }
 *    });
 */

(function(window, document, $) {
    $(document).on('init.dt', function(e, dtSettings) {
        if ( e.namespace !== 'dt' ) {
            return;
        }
        function addSelectOptions(){
            aData = ['Active', 'Archived', 'All']
            var r='<label><div class"input-group"><select class="form-control select-sm" id="archive-filter">', i, iLen=aData.length;
            for ( i=0 ; i<iLen ; i++ )
            {
                r += '<option value="'+aData[i]+'">'+aData[i]+'</option>';
            }
            return r+'</select></div></label>';
        }
        dtSettings.nTableWrapper.childNodes[0].childNodes[0].innerHTML += addSelectOptions()

        var table = $('#DataTables_Table_0').DataTable();
        table.columns(2).search('False').draw();

        $('input').on( 'keyup', function () {
            table.search( this.value ).draw();
        } );

        $('#archive-filter').change(function () {
            table.search('').draw();
            value = $('#archive-filter').val()
            if (value == 'All'){
                search = ''
            }
            else if (value == 'Archived'){
                search = 'True'
            }
            else {
                search = 'False'
            }
            table.columns(2).search( search ).draw();
        } );

        var options = dtSettings.oInit.conditionalPaging;
        if ($.isPlainObject(options) || options === true) {
            var config = $.isPlainObject(options) ? options : {},
                api = new $.fn.dataTable.Api(dtSettings),
                speed = 'slow',
                conditionalPaging = function(e) {
                    var $paging = $(api.table().container()).find('div.dataTables_paginate'),
                        pages = api.page.info().pages;

                    if (e instanceof $.Event) {
                        if (pages <= 1) {
                            if (config.style === 'fade') {
                                $paging.stop().fadeTo(speed, 0);
                            }
                            else {
                                $paging.css('visibility', 'hidden');
                            }
                        }
                        else {
                            if (config.style === 'fade') {
                                $paging.stop().fadeTo(speed, 1);
                            }
                            else {
                                $paging.css('visibility', '');
                            }
                        }
                    }
                    else if (pages <= 1) {
                        if (config.style === 'fade') {
                            $paging.css('opacity', 0);
                        }
                        else {
                            $paging.css('visibility', 'hidden');
                        }
                    }
                };

            if ($.isNumeric(config.speed) || $.type(config.speed) === 'string') {
                speed = config.speed;
            }

            conditionalPaging();

            api.on('draw.dt', conditionalPaging);
        }
    });
})(window, document, jQuery);