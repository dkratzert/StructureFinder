elements = ['X', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr',
    'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
    'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
    'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
    'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
    'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
    'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es'];

$(document).ready(function ($) {

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

    $.get(url = cgifile + '/cellcheck', function (result) {
        if (result === 'true') {
            $("#cellsearchcsd_button").removeClass('invisible');
        }
    });

    $.get(url = cgifile + '/version', function (result) {
        document.getElementById("version").innerHTML = result;
    });

    // toggle for cell tooltip
    $('[data-toggle="cell_tooltip"]').tooltip();

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

    mygrid = $('#mygrid');

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
    let b = $(window).height();
    let h = b * 0.35;
    if (h < 200) {
        h = 220;
    }
    // Define the grid height to 35% of the screen:
    mygrid.css("height", h);
    // w2ui 2.0 does not render the grid in the constructor:
    mygrid_obj.render(mygrid[0]);

    // Do advanced search:
    let advanced_search_button = $("#advsearch-button");
    advanced_search_button.click(function (event) {
        let txt_in = document.getElementById("text_in").value;
        let txt_out = document.getElementById("text_out").value;
        let elements_in = document.getElementById("elements_in").value;
        let elements_out = document.getElementById("elements_out").value;
        let cell_adv = document.getElementById("cell_adv").value;
        let more_res = $('#more_results').is(':checked');
        let supercell = $('#supercells').is(':checked');
        let onlyelem = $('#onlythese_elem').is(':checked');
        let datefield1 = document.getElementById("date1").value;
        let datefield2 = document.getElementById("date2").value;
        let itnum = $("#IT_number").val().split(" ")[0];
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
            if ($.inArray(el, outlist) >= 0) {
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
        let elinform = $("#elements_in.form-control");
        let elexform = $("#elements_out.form-control");
        elinform.css("color", "#f35e59");
        elinform.css("font-weight", "bold");
        elexform.css("color", "#f35e59");
        elexform.css("font-weight", "bold");
    }

    function elements_regular() {
        let elinform = $("#elements_in.form-control");
        let elexform = $("#elements_out.form-control");
        elinform.css("color", "#000000");
        elinform.css("font-weight", "normal");
        elexform.css("color", "#000000");
        elexform.css("font-weight", "normal");
    }

    function validate_element_input() {
        if (!check_elin() || !check_elex()) {
            elements_red();
        } else {
            elements_regular();
        }

    }

    // Validators for chemical elemets included search field:
    $("#elements_in").keyup(function () {
        validate_element_input();
    });

    // Validators for chemical elemets excluded search field:
    $("#elements_out").keyup(function () {
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
            if ($.inArray(el, elements) === -1) {
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
    var more_info_button = $('#more_info_badge');
    more_info_button.click(function () {
        var button_text = more_info_button.text();
        $("#more-cell-info").toggle(1);
    });

    $('#all_structures').click(function () {
        w2ui['mygrid'].reload(
            function (result) {
                displayresultnum(result);
                //console.log(result);
            });
    });

    // Switch between grow and fuse:
    $('#growCheckBox').click(function () {
        grow_enabled = this.checked;
        $("#moleculecolumn").attr('title', grow_enabled ? 'Completed Molecule' : 'Asymmetric Unit');
        if (molviewer) {
            molviewer.setGrow(grow_enabled);
        }
    });

    // Switch between advanced and simple search:
    var advbutton = $('#toggle_advsearch-button');
    advbutton.click(function () {
        var button_text = advbutton.text();
        $("#mainsearch").toggle(1);
        if (button_text.split(" ")[0] === "Advanced") {
            advbutton.html("Simple Search");
            document.getElementById("cell_adv").value = document.getElementById("smpl_cellsrch").value;
        } else {
            advbutton.html("Advanced Search");
            document.getElementById("smpl_cellsrch").value = document.getElementById("cell_adv").value;
        }
    });

    // Text search Button clicked:
    $("#smpl_textsrchbutton").click(function (event) {
        var txt = document.getElementById("smpl_textsrch").value;
        txtsearch(txt);
        //console.log(txt);
    });

    // Cell search Button clicked:
    $("#smpl_cellsrchbutton").click(function (event) {
        var cell = document.getElementById("smpl_cellsrch").value;
        cellsearch(cell);
    });

    // Enter key pressed in the simple text search field:
    $('#smpl_textsrch').keypress(function (e) {
        if (e.which === 13) {  // enter key
            var txt = document.getElementById("smpl_textsrch").value;
            txtsearch(txt);
            //console.log(txt);
        }
    });

    // Enter key pressed in the simple cell search field:
    $('#smpl_cellsrch').keypress(function (e) {
        if (e.which === 13) {  // enter key
            var cell = document.getElementById("smpl_cellsrch").value;
            cellsearch(cell);
            //console.log(cell);
        }
    });

    // Enter key pressed in one of the advanced search fields:
    $('#adv-search').keypress(function (e) {
        if (e.which === 13) {  // enter key
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
        $("#cellrow").removeClass('invisible');
        $("#cell_copy_btn").addClass('invisible');
        $("#growCheckBoxgroup").addClass('invisible');
        $("#moleculecolumn").addClass('invisible');
        $("#all_residuals").addClass('invisible');
        //$("#residualstable2").addClass('invisible');
        //$("#residuals").addClass('invisible');
        document.getElementById("cellrow").innerHTML = "Found " + numresult + " structures";
    }

    function display_molecule(structure) {
        var molcol = $("#moleculecolumn");
        if (!structure || !structure.atoms || structure.atoms.length === 0) {
            molcol.addClass('invisible');
            return;
        }
        var tbl = $('#residualstable2');
        // The residuals table is filled asynchronously, so keep the CSS default
        // height until it has a sensible size. The canvas fills this container.
        var height = tbl.height() - 20;
        if (height > 100) {
            molcol.css("height", height);
        }
        molcol.removeClass('invisible');
        if (!molviewer) {
            molviewer = Fastmolwidget.createViewer(molcol[0], null, molecule_options);
            // Only sets the flag, there is no structure to refresh yet:
            molviewer.setGrow(grow_enabled);
        }
        // loadStructure() honours the grow state kept in sync by the checkbox:
        molviewer.loadStructure(structure);
        molcol.attr('title', grow_enabled ? 'Completed Molecule' : 'Asymmetric Unit');
        molviewer.fit();
        molviewer.widget.fitToView();
    }

    function showprop(idstr) {
        /*
        This function uses AJAX POST calls to get the data of a structure and displays
        them below the main table.
        */
        $("#all_residuals").removeClass('invisible');
        // Uncheck the grow button:
        //$('#growCheckBox').prop("checked", false);
        var data;
        // Get residuals table 1:
        $.post(url = cgifile + '/residuals', data = {id: idstr, residuals1: true}, function (result) {
            document.getElementById("residualstable1").innerHTML = result;
        });

        // Get residuals table 2:
        $.post(url = cgifile + '/residuals', data = {id: idstr, residuals2: true}, function (result) {
            document.getElementById("residualstable2").innerHTML = result;
        });

        // Get unit cell row:
        $.post(url = cgifile + '/residuals', data = {id: idstr, unitcell: true}, function (result) {
            $("#cellrow").removeClass('invisible');
            $("#growCheckBoxgroup").removeClass('invisible');
            $("#cell_copy_btn").removeClass('invisible');
            document.getElementById("cellrow").innerHTML = result;

            var clipboard = new Clipboard('.btn');
            clipboard.on('success',
                function (e) {
                    e.clearSelection();
                }
            );
        });

        // display the big cif data table:
        $.post(url = cgifile + '/residuals', data = {id: idstr, all: true},
            function (result) {
                document.getElementById("residuals").innerHTML = result;
            }
        );

        // Get molecule data and display the molecule:
        $.post(url = cgifile + '/molecule', data = {id: idstr}, function (result) {
            display_molecule(result)
        });
    }

    // some options for the fastmolwidget viewer:
    var bgcolor = $(this.body).css("background-color");
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
        var url;
        w2ui['mygrid'].request('load', gridparams,
            url = cgifile + "/adv_srch",
            function (result) {
                displayresultnum(result);
                //console.log(result);
            }
        );
    }

    // Search for structures of last month:
    $('#lastmsearchlink').click(function () {
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
            if (!$.isNumeric(array[i])) {
                isal = false;
            }
        }
        return isal;
    }

    function cellsearch(cell) {
        var more_res = $('#more_results').is(':checked');
        var supercell = $('#supercells').is(':checked');
        cell = cell.replace(/\s+/g, ' ').trim();  // replace multiple spaces with one
        cell = cell.replace(/,/g, '.');  // replace comma with point
        //console.log(cell);
        var params;
        var url;
        if (isValidCell(cell)) {
            w2ui['mygrid'].request('load',
                params = {cell_search: cell, more: more_res, supercell: supercell},
                url = cgifile + "/cellsrch",
                function (result) {
                    displayresultnum(result);
                    //console.log(result.total);
                    //console.log(more_res);
                }
            );
        }
    }

    function txtsearch(text) {
        var advanced = false;
        var params;
        var url;
        //console.log(text+' in txtsearch');
        w2ui['mygrid'].request('load',
            params = {text_search: text},
            url = cgifile + "/txtsrch",
            function (result) {
                displayresultnum(result);
                //console.log(result);
            }
        );
    }

});
