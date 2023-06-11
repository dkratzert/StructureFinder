
$(document).ready(function($){

    let my_ccdc_grid = $('#my_ccdc_grid');

    // The main structures table:
    my_ccdc_grid.w2grid({
        name: 'my_ccdc_grid',
        header: 'StructureFinder',
        url: cgifile+"/csd-list",
        method: 'POST',
        show: {
            toolbar: false,
            footer: true
        },
        columns: [
            {field: 'chemical_formula',  caption: 'Formula', size: '20%', sortable: false, attr: 'align=left'},
            {field: 'cell_length_a',     caption: '<i>a</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_b',     caption: '<i>b</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_c',     caption: '<i>c</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_alpha',  caption: '<i>&alpha;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_beta',   caption: '<i>&beta;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_gamma',  caption: '<i>&gamma;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'recid',             caption: 'Itentity', size: '10%',  sortable: false, resizable: true},
            {field: 'space_group',     caption: 'Space Group', size: '10%',  sortable: false, resizable: true}
        ],
        //sortData: [{field: 'dataname', direction: 'ASC'}],
        onDblClick:function(event) {
            let strid = event.recid;
            show_csd_entry(strid);
            //console.log(event);
        }
    });

    //gets the window's height
    let bc = $(window).height();
    let hc = bc * 0.50;
    if (hc < 220) {
        hc = 220;
    }
    // Define the grid height to 35% of the screen:
    my_ccdc_grid.css("height", hc);


    function csdcellsearch(cell) {
        //var more_res = $('#more_results').is(':checked');
        let e = document.getElementById("centering_drop");
        let centering = e.options[e.selectedIndex].value;
        //console.log(centering+' #centering##');
        cell = cell.replace(/\s+/g, ' ').trim();  // replace multiple spaces with one
        cell = cell.replace(/,/g, '.');  // replace comma with point
        //console.log(cell+'csdcellsrch');
        let params;
        let url;
        if (isValidCell(cell)) {
            w2ui['my_ccdc_grid'].request('get-records',
                {cell: cell, centering: centering, str_id: strid},
                cgifile + "/csd-list",  // the 'get-records' request of w2ui fetches the CSD entries found by 'params'
                function (result) {
                    display_csd_resultnum(result);
                    //console.log(result);
                    //console.log(more_res);
                }
            );
        }
    }
    
    
    $('#filter_button').click(function(event) {
        refine_elements(elements);    
    });
    
    function refine_elements(elements) {
        my_ccdc_grid.select(0);
        //my_ccdc_grid.remove(0);
        my_ccdc_grid.hide();
    }

    // display how many results I got
    function display_csd_resultnum(result) {
        let numresult;
        if (typeof result === 'undefined') numresult = 0;
        else (numresult = result.total);
        document.getElementById("found_csd").innerHTML = "Found " + numresult + " structures";
    }
    
    function show_csd_entry(identifier) {
        //console.log(identifier);
        let win = window.open('https://www.ccdc.cam.ac.uk/structures/Search?entry_list=' + identifier, '_blank');
        win.focus();
    }

        // Test if a valid unit cell is in cell:
    function isValidCell(cell) {
        let scell = cell.split(" ");
        //console.log(scell);
        if (isNumericArray(scell)) {
            return !(scell.length !== 6); // return True if 6 values
        } else {
            return false;
        }
    }

    // Test if all values in array are numeric:
    function isNumericArray(array) {
        let isal = true;
        for (const element of array) {
            if (!$.isNumeric(element)) {
                isal = false;
            }
        }
        return isal;
    }
    
    
    // Cell search Button clicked:
    $("#csd_search_btn").click(function(event) {
        let cell = document.getElementById("cell_csd_inp").value;
        //console.log(cell+' btnsrch');
        csdcellsearch(cell);
    });

    
    // Enter key pressed in the cell search field:
    $('#cell_csd_inp').keypress(function(e) {
        if (e.which === 13) {  // enter key
            let cell = document.getElementById("cell_csd_inp").value;
            csdcellsearch(cell);
            //console.log(txt);
        }
    });

});