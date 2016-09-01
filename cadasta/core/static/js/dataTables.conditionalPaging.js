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
        console.log(e, dtSettings)
        // console.log(dtSettings.oTableWrapper)

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

// (function($) {
/*
 * Function: fnGetColumnData
 * Purpose:  Return an array of table values from a particular column.
 * Returns:  array string: 1d data array
 * Inputs:   object:oSettings - dataTable settings object. This is always the last argument past to the function
 *           int:iColumn - the id of the column to extract the data from
 *           bool:bUnique - optional - if set to false duplicated values are not filtered out
 *           bool:bFiltered - optional - if set to false all the table data is used (not only the filtered)
 *           bool:bIgnoreEmpty - optional - if set to false empty values are not filtered from the result array
 * Author:   Benedikt Forchhammer <b.forchhammer /AT\ mind2.de>
 */
// $.fn.dataTableExt.oApi.fnGetColumnData = function ( oSettings, iColumn, bUnique, bFiltered, bIgnoreEmpty ) {
//     // check that we have a column id
//     if ( typeof iColumn == "undefined" ) return new Array();
     
//     // by default we only want unique data
//     if ( typeof bUnique == "undefined" ) bUnique = true;
     
//     // by default we do want to only look at filtered data
//     if ( typeof bFiltered == "undefined" ) bFiltered = true;
     
//     // by default we do not want to include empty values
//     if ( typeof bIgnoreEmpty == "undefined" ) bIgnoreEmpty = true;
     
//     // list of rows which we're going to loop through
//     var aiRows;
     
//     // use only filtered rows
//     if (bFiltered == true) aiRows = oSettings.aiDisplay;
//     // use all rows
//     else aiRows = oSettings.aiDisplayMaster; // all row numbers
 
//     // set up data array   
//     var asResultData = new Array();
     
//     for (var i=0,c=aiRows.length; i<c; i++) {
//         iRow = aiRows[i];
//         var aData = this.fnGetData(iRow);
//         var sValue = aData[iColumn];
         
//         // ignore empty values?
//         if (bIgnoreEmpty == true && sValue.length == 0) continue;
 
//         // ignore unique values?
//         else if (bUnique == true && jQuery.inArray(sValue, asResultData) > -1) continue;
         
//         // else push the value onto the result data array
//         else asResultData.push(sValue);
//     }
     
//     return asResultData;
// }}(jQuery));
 
 
// function fnCreateSelect( aData )
// {
//     aData = ['Active', 'Archived', 'All']
//     var r='<select><option value=""></option>', i, iLen=aData.length;
//     for ( i=0 ; i<iLen ; i++ )
//     {
//         r += '<option value="'+aData[i]+'">'+aData[i]+'</option>';
//     }
//     return r+'</select>';
// }

// (function(window, document, $) {
//     $(document).ready(function() {
//         /* Initialise the DataTable */
//         console.log('document is ready.')
//         if ( $.fn.dataTable.isDataTable( '#example' ) ) {
//             table = $('#example').DataTable();
//         }
//         else {
//             table = $('#example').DataTable( {
//                 paging: false
//             } );
//         }
//         // var oTable = $('#example').dataTable( {
//         //     "oLanguage": {
//         //         "sSearch": "Search all columns:"
//         //     },
//         //     initComplete: function(settings, json) {
//         //         console.log( 'DataTables has finished its initialisation.' );
//         //       }
//         // } );
//         /* Add a select menu for each TH element in the table footer */
//         // $('#example').dataTable( {
              
//         //     } );

//         // $("div #DataTables_Table_0_filter").each( function ( i ) {
//         //         console.log('inside thead')
//         //         console.log(i)
//         //         this.innerHTML = (fnCreateSelect(['Active', 'Archived', 'All']));
//         //         $('select', this).change( function () {
//         //             oTable.fnFilter( $(this).val(), i );
//         //         } );
//         //     } );
//     } );
// }) (window, document, jQuery)