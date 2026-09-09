elements = ['X', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr',
    'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
    'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
    'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
    'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
    'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
    'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es'];

// Equivalent of jQuery's $.isNumeric():
function isNumeric(value) {
    return !isNaN(parseFloat(value)) && isFinite(value);
}

// Toggles an element's visibility, equivalent in effect to the previous
// jQuery $(el).toggle(1) call. Elements using Bootstrap's ".collapse" class
// (display:none by default) are toggled via the ".show" class Bootstrap 5
// expects; plain elements are toggled via their inline "display" style.
function toggleDisplay(el) {
    if (el.classList.contains('collapse')) {
        el.classList.toggle('show');
    } else if (getComputedStyle(el).display === 'none') {
        el.style.display = '';
    } else {
        el.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function () {

    var d1 = document.getElementById('date1');
    var d2 = document.getElementById('date2');
    if (d1 && d2) {
        // w2ui 2.0 needs the elements themselves, "start"/"end" strings are dates:
        new w2field('date', {format: 'yyyy-mm-dd', end: d2}).render(d1);
        new w2field('date', {format: 'yyyy-mm-dd', start: d1}).render(d2);
    }

    // The structure ID
    var strid = null;
    // The fastmolwidget viewer instance
    var molviewer = null;
    // Grow is on by default, see the growCheckBox in the template:
    var grow_enabled = true;

    fetch(cgifile + '/cellcheck')
        .then(function (response) { return response.text(); })
        .then(function (result) {
            if (result === 'true') {
                document.getElementById("cellsearchcsd_button").classList.remove('invisible');
            }
        });

    fetch(cgifile + '/version')
        .then(function (response) { return response.text(); })
        .then(function (result) {
            document.getElementById("version").innerHTML = result;
        });

    // Enable Bootstrap tooltips for elements that request one:
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // The record id of a w2ui 2.0 selection event. Depending on how the row was
    // selected, the id is either in "recid" or below "clicked".
    function selected_recid(event) {
        var detail = event.detail || {};
        if (detail.recid !== undefined && detail.recid !== null) {
            return detail.recid;
        }
        var clicked = detail.clicked || {};
        if (clicked.recid !== undefined && clicked.recid !== null) {
            return clicked.recid;
        }
        if (clicked.recids && clicked.recids.length > 0) {
            return clicked.recids[0];
        }
        return null;
    }

    let mygrid = document.getElementById('mygrid');

    // The main structures table:
    var mygrid_obj = new w2grid({
        name: 'mygrid',
        header: 'StructureFinder',
        url: cgifile + "/all",
        // Send the search parameters as plain query values, not wrapped in a
        // "request" JSON parameter as the w2ui default HTTPJSON would do:
        dataType: 'HTTP',
        show: {
            toolbar: false,
            footer: true
        },
        columns: [
            {field: 'recid', text: 'ID', size: '45px', sortable: false, attr: 'align=center'},
            {field: 'dataname', text: 'Data Name', size: '15%', sortable: false, resizable: true},
            {field: 'filename', text: 'File Name', size: '20%', sortable: false, resizable: true},
            {field: 'modification_time', text: 'Last Modified', size: '10%', sortable: false, resizable: true},
            {field: 'path', text: 'Path', size: '65%', sortable: false, resizable: true}
        ],
        //sortData: [{field: 'modification_time', direction: 'ASC'}],
        onSelect: function (event) {
            var recid = selected_recid(event);
            if (recid === null) {
                return;
            }
            strid = recid;
            showprop(strid);
        }
    });

    //gets the window's height
    let b = window.innerHeight;
    let h = b * 0.35;
    if (h < 200) {
        h = 220;
    }
    // Define the grid height to 35% of the screen:
    mygrid.style.height = h + 'px';
    // w2ui 2.0 does not render the grid in the constructor:
    mygrid_obj.render(mygrid);

    // Do advanced search:
    let advanced_search_button = document.getElementById("advsearch-button");
    advanced_search_button.addEventListener('click', function (event) {
        let txt_in = document.getElementById("text_in").value;
        let txt_out = document.getElementById("text_out").value;
        let elements_in = document.getElementById("elements_in").value;
        let elements_out = document.getElementById("elements_out").value;
        let cell_adv = document.getElementById("cell_adv").value;
        let more_res = document.getElementById('more_results').checked;
        let supercell = document.getElementById('supercells').checked;
        let onlyelem = document.getElementById('onlythese_elem').checked;
        let datefield1 = document.getElementById("date1").value;
        let datefield2 = document.getElementById("date2").value;
        let itnum = document.getElementById("IT_number").value.split(" ")[0];
        let r1val = document.getElementById("r1_val_adv").value;
        let ccdc_num = document.getElementById("ccdc_num_adv").value;
        advanced_search(txt_in, txt_out, elements_in, elements_out, cell_adv, more_res,
            supercell, datefield1, datefield2, itnum, onlyelem, r1val, ccdc_num);
    });

    function get_cell_from_p4p(p4pdata) {
        let cell = '';
        //console.log('insidep4p');
        let allLines = p4pdata.split(/\r\n|\n|\r/);
        // Reading line by line
        //console.log(allLines);
        for (const element of allLines) {
            let spline = element.split(/\s+/);
            //console.log(spline);
            if (spline[0] === 'CELL') {
                cell += spline[1] + '  ';
                cell += spline[2] + '  ';
                cell += spline[3] + '  ';
                cell += spline[4] + '  ';
                cell += spline[5] + '  ';
                cell += spline[6];
            }
            //console.log(cell);
            document.getElementById('smpl_cellsrch').value = cell;
            document.getElementById('cell_adv').value = cell;
        }
    }

    function get_cell_from_res(resdata) {
        let cell = '';
        //console.log('insidep4p');
        let allLines = resdata.split(/\r\n|\n|\r/);
        for (const element of allLines) {
            let spline = element.split(/\s+/);
            if (spline[0] === 'CELL') {
                cell += spline[2] + '  ';
                cell += spline[3] + '  ';
                cell += spline[4] + '  ';
                cell += spline[5] + '  ';
                cell += spline[6] + '  ';
                cell += spline[7];
            }
            //console.log(cell);
            document.getElementById('smpl_cellsrch').value = cell;
            document.getElementById('cell_adv').value = cell;
        }
    }


    function get_cell_from_cif(cifdata) {
        let cell = '';
        //_cell_length_a                   11.776(2)
        //_cell_length_b                   5.7561(12)
        //_cell_length_c                   17.462(4)
        //_cell_angle_alpha                90.00
        //_cell_angle_beta                 95.02(3)
        //_cell_angle_gamma                90.00
        let allLines = cifdata.split(/\r\n|\n|\r/);
        for (const element of allLines) {
            let spline = element.split(/\s+/);
            if (spline[0] === '_cell_length_a') {
                cell += spline[1].split('(')[0] + '  ';
            }
            if (spline[0] === '_cell_length_b') {
                cell += spline[1].split('(')[0] + '  ';
            }
            if (spline[0] === '_cell_length_c') {
                cell += spline[1].split('(')[0] + '  ';
            }
            if (spline[0] === '_cell_angle_alpha') {
                cell += spline[1].split('(')[0] + '  ';
            }
            if (spline[0] === '_cell_angle_beta') {
                cell += spline[1].split('(')[0] + '  ';
            }
            if (spline[0] === '_cell_angle_gamma') {
                cell += spline[1].split('(')[0] + '  ';
            }
            //console.log(cell);
            document.getElementById('smpl_cellsrch').value = cell;
            document.getElementById('cell_adv').value = cell;
        }
    }


    let dropZone = document.getElementById('dropZone');

    dropZone.addEventListener('dragover', function (e) {
        e.stopPropagation();
        e.preventDefault();
        //e.dataTransfer.dropEffect = 'copy';
    });

    // Get file data on drop
    dropZone.addEventListener('drop', function (e) {
        e.stopPropagation();
        e.preventDefault();
        let files = e.dataTransfer.files; // Array of all files
        //console.log('dropped');
        if (files[0].type.match(/.*/)) {
            let reader = new FileReader();

            reader.onload = function (e2) {
                // finished reading file data.
                var txt = e2.target.result;
                if (files[0].name.split('.').pop() === 'p4p') {
                    get_cell_from_p4p(txt);
                }
                if (files[0].name.split('.').pop().match('res|ins')) {
                    get_cell_from_res(txt);
                }
                if (files[0].name.split('.').pop() === 'cif') {
                    get_cell_from_cif(txt);
                }
            };

            reader.readAsText(files[0], "ASCII"); // start reading the file data.
        }
    });


    // Check if element names are occouring more than one time:
    function is_elem_doubled(elements_in, elements_out) {
        let sumlist = elements_in.split(" ");
        let outlist = elements_out.split(" ");
        let ok = true;
        ok = validateSumForm(elements_in);
        for (const element of sumlist) {
            let el = element;
            if (outlist.includes(el)) {
                // A space character is allowed:
                if (el === "") {
                    continue
                }
                ok = false;
            }
        }
        return ok;
    }

    function check_elin() {
        let elements_in = document.getElementById("elements_in").value;
        let elements_out = document.getElementById("elements_out").value;
        return is_elem_doubled(elements_in, elements_out);
    }

    function check_elex() {
        let elements_in = document.getElementById("elements_in").value;
        let elements_out = document.getElementById("elements_out").value;
        return is_elem_doubled(elements_out, elements_in)
    }

    function elements_red() {
        let elinform = document.querySelector("#elements_in.form-control");
        let elexform = document.querySelector("#elements_out.form-control");
        elinform.style.color = "#f35e59";
        elinform.style.fontWeight = "bold";
        elexform.style.color = "#f35e59";
        elexform.style.fontWeight = "bold";
    }

    function elements_regular() {
        let elinform = document.querySelector("#elements_in.form-control");
        let elexform = document.querySelector("#elements_out.form-control");
        elinform.style.color = "#000000";
        elinform.style.fontWeight = "normal";
        elexform.style.color = "#000000";
        elexform.style.fontWeight = "normal";
    }

    function validate_element_input() {
        if (!check_elin() || !check_elex()) {
            elements_red();
        } else {
            elements_regular();
        }

    }

    // Validators for chemical elemets included search field:
    document.getElementById("elements_in").addEventListener('keyup', function () {
        validate_element_input();
    });

    // Validators for chemical elemets excluded search field:
    document.getElementById("elements_out").addEventListener('keyup', function () {
        validate_element_input();
    });

    function validateSumForm(sumform) {
        // Validates if sumform contains only valid chemical elements
        // Space characters are allowed
        var ok = true;
        //console.log(sumform);
        if (sumform.length === 0) {
            return true;
        }
        var sumlist = sumform.split(" ");
        //console.log(sumlist);
        for (var i = 0; i < sumlist.length; i++) {
            var el = sumlist[i];
            //console.log(el);
            if (!elements.includes(el)) {
                // A space character is allowed:
                if (el.length === 0) {
                    continue
                }
                ok = false;
            }
        }
        return ok;
    }

    // Toggle search info:
    var more_info_button = document.getElementById('more_info_badge');
    more_info_button.addEventListener('click', function () {
        toggleDisplay(document.getElementById("more-cell-info"));
    });

    document.getElementById('all_structures').addEventListener('click', function () {
        w2ui['mygrid'].reload(
            function (result) {
                displayresultnum(result);
                //console.log(result);
            });
    });

    // Switch between grow and fuse:
    document.getElementById('growCheckBox').addEventListener('click', function () {
        grow_enabled = this.checked;
        document.getElementById("moleculecolumn").setAttribute('title', grow_enabled ? 'Completed Molecule' : 'Asymmetric Unit');
        if (molviewer) {
            molviewer.setGrow(grow_enabled);
        }
    });

    // Switch between advanced and simple search:
    var advbutton = document.getElementById('toggle_advsearch-button');
    advbutton.addEventListener('click', function () {
        var button_text = advbutton.textContent;
        toggleDisplay(document.getElementById("mainsearch"));
        if (button_text.split(" ")[0] === "Advanced") {
            advbutton.innerHTML = "Simple Search";
            document.getElementById("cell_adv").value = document.getElementById("smpl_cellsrch").value;
        } else {
            advbutton.innerHTML = "Advanced Search";
            document.getElementById("smpl_cellsrch").value = document.getElementById("cell_adv").value;
        }
    });

    // Text search Button clicked:
    document.getElementById("smpl_textsrchbutton").addEventListener('click', function (event) {
        var txt = document.getElementById("smpl_textsrch").value;
        txtsearch(txt);
        //console.log(txt);
    });

    // Cell search Button clicked:
    document.getElementById("smpl_cellsrchbutton").addEventListener('click', function (event) {
        var cell = document.getElementById("smpl_cellsrch").value;
        cellsearch(cell);
    });

    // Enter key pressed in the simple text search field:
    document.getElementById('smpl_textsrch').addEventListener('keypress', function (e) {
        if (e.which === 13 || e.key === 'Enter') {  // enter key
            var txt = document.getElementById("smpl_textsrch").value;
            txtsearch(txt);
            //console.log(txt);
        }
    });

    // Enter key pressed in the simple cell search field:
    document.getElementById('smpl_cellsrch').addEventListener('keypress', function (e) {
        if (e.which === 13 || e.key === 'Enter') {  // enter key
            var cell = document.getElementById("smpl_cellsrch").value;
            cellsearch(cell);
            //console.log(cell);
        }
    });

    // Enter key pressed in one of the advanced search fields:
    document.getElementById('adv-search').addEventListener('keypress', function (e) {
        if (e.which === 13 || e.key === 'Enter') {  // enter key
            advanced_search_button.click();
            //console.log(cell);
        }
    });

    // display how many results I got
    function displayresultnum(result) {
        var numresult;
        if (typeof result.total === 'undefined') {
            numresult = 0;
        } else {
            numresult = result.total;
        }
        document.getElementById("cellrow").classList.remove('invisible');
        document.getElementById("cell_copy_btn").classList.add('invisible');
        document.getElementById("growCheckBoxgroup").classList.add('invisible');
        document.getElementById("moleculecolumn").classList.add('invisible');
        document.getElementById("all_residuals").classList.add('invisible');
        //document.getElementById("residualstable2").classList.add('invisible');
        //document.getElementById("residuals").classList.add('invisible');
        document.getElementById("cellrow").innerHTML = "Found " + numresult + " structures";
    }

    function display_molecule(structure) {
        var molcol = document.getElementById("moleculecolumn");
        if (!structure || !structure.atoms || structure.atoms.length === 0) {
            molcol.classList.add('invisible');
            return;
        }
        var tbl = document.getElementById('residualstable2');
        // The residuals table is filled asynchronously, so keep the CSS default
        // height until it has a sensible size. The canvas fills this container.
        var height = tbl.offsetHeight - 20;
        if (height > 100) {
            molcol.style.height = height + 'px';
        }
        molcol.classList.remove('invisible');
        if (!molviewer) {
            molviewer = Fastmolwidget.createViewer(molcol, null, molecule_options);
            // Only sets the flag, there is no structure to refresh yet:
            molviewer.setGrow(grow_enabled);
        }
        // loadStructure() honours the grow state kept in sync by the checkbox:
        molviewer.loadStructure(structure);
        molcol.setAttribute('title', grow_enabled ? 'Completed Molecule' : 'Asymmetric Unit');
        molviewer.fit();
        molviewer.widget.fitToView();
    }

    function postForm(url, data) {
        var body = new URLSearchParams();
        for (var key in data) {
            body.append(key, data[key]);
        }
        return fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: body
        });
    }

    function showprop(idstr) {
        /*
        This function uses fetch() POST calls to get the data of a structure and displays
        them below the main table.
        */
        document.getElementById("all_residuals").classList.remove('invisible');
        // Uncheck the grow button:
        //document.getElementById('growCheckBox').checked = false;

        // Get residuals table 1:
        postForm(cgifile + '/residuals', {id: idstr, residuals1: true})
            .then(function (response) { return response.text(); })
            .then(function (result) {
                document.getElementById("residualstable1").innerHTML = result;
            });

        // Get residuals table 2:
        postForm(cgifile + '/residuals', {id: idstr, residuals2: true})
            .then(function (response) { return response.text(); })
            .then(function (result) {
                document.getElementById("residualstable2").innerHTML = result;
            });

        // Get unit cell row:
        postForm(cgifile + '/residuals', {id: idstr, unitcell: true})
            .then(function (response) { return response.text(); })
            .then(function (result) {
                document.getElementById("cellrow").classList.remove('invisible');
                document.getElementById("growCheckBoxgroup").classList.remove('invisible');
                document.getElementById("cell_copy_btn").classList.remove('invisible');
                document.getElementById("cellrow").innerHTML = result;

                var clipboard = new Clipboard('.btn');
                clipboard.on('success',
                    function (e) {
                        e.clearSelection();
                    }
                );
            });

        // display the big cif data table:
        postForm(cgifile + '/residuals', {id: idstr, all: true})
            .then(function (response) { return response.text(); })
            .then(function (result) {
                document.getElementById("residuals").innerHTML = result;
            });

        // Get molecule data and display the molecule:
        postForm(cgifile + '/molecule', {id: idstr})
            .then(function (response) { return response.json(); })
            .then(function (result) {
                display_molecule(result)
            });
    }

    // some options for the fastmolwidget viewer:
    var bgcolor = getComputedStyle(document.body).backgroundColor;
    var molecule_options = {
        controls: false,
        background: bgcolor,
        adps: false,
        labels: false,
        bondWidth: 3
    };

    function advanced_search(text_in, text_out, elements_in, elements_out, cell_adv, more_res, supercell,
                             date1, date2, itnum, onlyelem, r1val, ccdc_num) {
        var cell = cell_adv.replace(/\s+/g, ' ').trim();
        cell = cell.replace(/,/g, '.');  // replace comma with point
        if (!isValidCell(cell)) {
            cell = "";
        }
        var gridparams = {
            cell_search: cell, text_in: text_in, text_out: text_out, elements_in: elements_in,
            elements_out: elements_out, more: more_res, supercell: supercell, date1: date1, date2: date2
            , it_num: itnum, onlyelem: onlyelem, r1val: r1val, ccdc_num: ccdc_num
        };
        //console.log(gridparams);
        w2ui['mygrid'].request('load', gridparams,
            cgifile + "/adv_srch",
            function (result) {
                displayresultnum(result);
                //console.log(result);
            }
        );
    }

    // Search for structures of last month:
    document.getElementById('lastmsearchlink').addEventListener('click', function () {
        var date_now = new Date();
        var month = date_now.getUTCMonth();
        var day = date_now.getUTCDate();
        var lastmonth = new Date(date_now.getUTCFullYear(), month - 1, day);
        var lastmdate = lastmonth.toISOString().split("T")[0];
        //console.log(lastmdate+ ' '+ date_now.toISOString().split("T")[0]);
        // From last month to now():
        advanced_search("", "", "", "", "", "", "", lastmdate, date_now.toISOString().split("T")[0]);
    });

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
        for (var i = 0; i < array.length; i++) {
            if (!isNumeric(array[i])) {
                isal = false;
            }
        }
        return isal;
    }

    function cellsearch(cell) {
        var more_res = document.getElementById('more_results').checked;
        var supercell = document.getElementById('supercells').checked;
        cell = cell.replace(/\s+/g, ' ').trim();  // replace multiple spaces with one
        cell = cell.replace(/,/g, '.');  // replace comma with point
        //console.log(cell);
        if (isValidCell(cell)) {
            w2ui['mygrid'].request('load',
                {cell_search: cell, more: more_res, supercell: supercell},
                cgifile + "/cellsrch",
                function (result) {
                    displayresultnum(result);
                    //console.log(result.total);
                    //console.log(more_res);
                }
            );
        }
    }

    function txtsearch(text) {
        //console.log(text+' in txtsearch');
        w2ui['mygrid'].request('load',
            {text_search: text},
            cgifile + "/txtsrch",
            function (result) {
                displayresultnum(result);
                //console.log(result);
            }
        );
    }

});
