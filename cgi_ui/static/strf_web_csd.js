
$(document).ready(function($){

    my_ccdc_grid = $('#my_ccdc_grid');

    // The main structures table:
    my_ccdc_grid.w2grid({
        name: 'my_ccdc_grid',
        header: 'StructureFinder',
        url: cgifile+"/csd-list",
        method: 'GET',
        show: {
            toolbar: false,
            footer: true
        },
        columns: [
            {field: 'chemical_formula',  caption: 'formula', size: '20%', sortable: false, attr: 'align=left'},
            {field: 'cell_length_a',     caption: '<i>a</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_b',     caption: '<i>b</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_c',     caption: '<i>c</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_alpha',  caption: '<i>&alpha;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_beta',   caption: '<i>&beta;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_gamma',  caption: '<i>&gamma;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'recid',             caption: 'Itentity', size: '10%',  sortable: false, resizable: true},
            {field: 'space_group',     caption: 'Space Grp.', size: '10%',  sortable: false, resizable: true}
        ],
        //sortData: [{field: 'dataname', direction: 'ASC'}],
        onDblClick:function(event) {
            strid = event.recid;
            show_csd_entry(strid);
            //console.log(event);
        }
    });

    //gets the window's height
    var bc = $(window).height();
    var hc = bc * 0.50;
    if (hc < 220) {
        hc = 220;
    }
    // Define the grid height to 35% of the screen:
    my_ccdc_grid.css("height", hc);


    function csdcellsearch(cell) {
        //var more_res = $('#more_results').is(':checked');
        var e = document.getElementById("centering_drop");
        var centering = e.options[e.selectedIndex].value;
        //console.log(centering+' #centering##');
        cell = cell.replace(/\s+/g, ' ').trim();  // replace multiple spaces with one
        cell = cell.replace(/,/g, '.');  // replace comma with point
        //console.log(cell+'csdcellsrch');
        var params;
        var url;
        if (isValidCell(cell)) {
            w2ui['my_ccdc_grid'].request('get-records',
                params = {cell: cell, centering: centering},
                url = cgifile + "/csd-list",
                function (result) {
                    //displayresultnum(result);
                    //console.log(result);
                    //console.log(more_res);
                }
            );
        }
    }
    
    
    function show_csd_entry(identifier) {
        //console.log(identifier);
        var win = window.open('https://www.ccdc.cam.ac.uk/structures/Search?entry_list=' + identifier, '_blank');
        win.focus();
    }

        // Test if a valid unit cell is in cell:
    function isValidCell(cell) {
        var scell = cell.split(" ");
        //console.log(scell);
        if (isNumericArray(scell)) {
            return !(scell.length !== 6); // return True if 6 values
        } else {
            return false;
        }
    }

    // Test if all values in array are numeric:
    function isNumericArray(array) {
        var isal = true;
        for (var i=0; i<array.length; i++) {
            if (!$.isNumeric(array[i])) {
                isal = false;
            }
        }
        return isal;
    }
    
    
    // Cell search Button clicked:
    $("#csd_search_btn").click(function(event) {
        var cell = document.getElementById("cell_csd_inp").value;
        //console.log(cell+' btnsrch');
        csdcellsearch(cell);
    });

    
    // Enter key pressed in the cell search field:
    $('#cell_csd_inp').keypress(function(e) {
        if (e.which === 13) {  // enter key
            var cell = document.getElementById("cell_csd_inp").value;
            csdcellsearch(cell);
            //console.log(txt);
        }
    });

});