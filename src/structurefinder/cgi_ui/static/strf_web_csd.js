
document.addEventListener('DOMContentLoaded', function () {

    let my_ccdc_grid = document.getElementById('my_ccdc_grid');

    // The main structures table:
    let my_ccdc_grid_obj = new w2grid({
        name: 'my_ccdc_grid',
        header: 'StructureFinder',
        url: cgifile+"/csd-list",
        // Send the search parameters as plain query values, not wrapped in a
        // "request" JSON parameter as the w2ui default HTTPJSON would do:
        dataType: 'HTTP',
        show: {
            toolbar: false,
            footer: true
        },
        columns: [
            {field: 'chemical_formula',  text: 'Formula', size: '20%', sortable: false, attr: 'align=left'},
            {field: 'cell_length_a',     text: '<i>a</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_b',     text: '<i>b</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_length_c',     text: '<i>c</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_alpha',  text: '<i>&alpha;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_beta',   text: '<i>&beta;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'cell_angle_gamma',  text: '<i>&gamma;</i>', size: '10%',  sortable: false, resizable: true},
            {field: 'recid',             text: 'Itentity', size: '10%',  sortable: false, resizable: true},
            {field: 'space_group',     text: 'Space Group', size: '10%',  sortable: false, resizable: true}
        ],
        //sortData: [{field: 'dataname', direction: 'ASC'}],
        onDblClick:function(event) {
            let detail = event.detail || {};
            let recid = detail.recid;
            if (recid == null && detail.clicked) {
                recid = detail.clicked.recid;
            }
            if (recid != null) {
                show_csd_entry(recid);
            }
        }
    });

    //gets the window's height
    let bc = window.innerHeight;
    let hc = bc * 0.50;
    if (hc < 220) {
        hc = 220;
    }
    // Define the grid height to 35% of the screen:
    my_ccdc_grid.style.height = hc + 'px';
    // w2ui 2.0 does not render the grid in the constructor:
    my_ccdc_grid_obj.render(my_ccdc_grid);


    function csdcellsearch(cell) {
        //var more_res = document.getElementById('more_results').checked;
        let e = document.getElementById("centering_drop");
        let centering = e.options[e.selectedIndex].value;
        //console.log(centering+' #centering##');
        cell = cell.replace(/\s+/g, ' ').trim();  // replace multiple spaces with one
        cell = cell.replace(/,/g, '.');  // replace comma with point
        //console.log(cell+'csdcellsrch');
        if (isValidCell(cell)) {
            w2ui['my_ccdc_grid'].request('load',
                {cell: cell, centering: centering, str_id: strid},
                cgifile + "/csd-list",  // the 'load' request of w2ui fetches the CSD entries found by 'params'
                function (result) {
                    display_csd_resultnum(result);
                    //console.log(result);
                    //console.log(more_res);
                }
            );
        }
    }


    let filter_button = document.getElementById('filter_button');
    if (filter_button) {
        filter_button.addEventListener('click', function (event) {
            refine_elements(elements);
        });
    }

    function refine_elements(elements) {
        w2ui['my_ccdc_grid'].select(0);
        //w2ui['my_ccdc_grid'].remove(0);
        my_ccdc_grid.style.display = 'none';
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
            if (!isNumeric(element)) {
                isal = false;
            }
        }
        return isal;
    }

    // Equivalent of jQuery's $.isNumeric():
    function isNumeric(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    }


    // Cell search Button clicked:
    document.getElementById("csd_search_btn").addEventListener('click', function (event) {
        let cell = document.getElementById("cell_csd_inp").value;
        //console.log(cell+' btnsrch');
        csdcellsearch(cell);
    });


    // Enter key pressed in the cell search field:
    document.getElementById('cell_csd_inp').addEventListener('keypress', function (e) {
        if (e.which === 13 || e.key === 'Enter') {  // enter key
            let cell = document.getElementById("cell_csd_inp").value;
            csdcellsearch(cell);
            //console.log(txt);
        }
    });

});
