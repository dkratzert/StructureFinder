<!-- Advanced search options (collapsible) -->
<div id="adv-search" class="collapse mb-3">
    <div class="row mb-2">
        <div class="col-12">
            <div class="btn-group btn-group-sm" role="group">
                <button type="button" class="badge bg-secondary" id="more_info_badge">info</button>
                <span>&nbsp;&nbsp;</span>
                <div class="form-check form-check-inline">
                    <input type="checkbox" class="form-check-input" id="more_results"
                           title="More cell search results">
                    <label class="form-check-label" for="more_results">More cell search results</label>
                </div>
                <span>&nbsp;&nbsp;</span>
                <div class="form-check form-check-inline">
                    <input type="checkbox" class="form-check-input" id="supercells"
                           title="Find supercells">
                    <label class="form-check-label" for="supercells">Find supercells</label>
                </div>
                <span>&nbsp;&nbsp;</span>
                %include('cgi_ui/views/spgr.tpl')
                Find by space group
            </div>
        </div>
    </div>

    <div id="more-cell-info" class="collapse mb-3">
        <div class="row">
            <div class="col-sm-6">
                <b>regular</b><br>
                volume: ±3 %, length: 0.06 Å, angle: 1.0°<br>
                <br>
                <b>more results option</b><br>
                volume: ±9 %, length: 0.2 Å, angle: 2.0°<br>
            </div>
            <div class="col-sm-6">
                <b>Supercells</b>
                <br>
                Find also unit cells of 1, 2, 3, 4, 6, 8, 10 times the volume.
                <br>
                <b>Space group search</b>
                <br>
                Be aware that not every cif file before SHELXL-2013 has a space group number. These will not be
                found.
            </div>
        </div>
    </div>

    <div class="row mb-2">
        <div class="col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text">Unit Cell</span>
                <input type="text" class="form-control" placeholder="a b c α β γ"
                       id="cell_adv">
            </div>
        </div>

        <div class="col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text"><i>R</i><sub>1</sub> <=</span>
                <input type="text" class="form-control" id="r1_val_adv">
                <span class="input-group-text">%</span>
            </div>
        </div>
    </div>
    <div class="row mb-2">
        <div class="col-sm-6">
            <div class="input-group input-group-sm w2ui-field">
                <span class="input-group-text" data-bs-toggle="tooltip"
                       title="Search for structures that were modified between two dates">Date from</span>
                <input class="form-control form-control-sm" title="Date" type="text" id="date1" style="width: 50%;">
                <span class="input-group-text">to</span>
                <input class="form-control form-control-sm" title="Date" type="text" id="date2" style="width: 50%;">
                <button type="button" class="btn btn-sm btn-outline-secondary"
                   data-bs-toggle="tooltip" title="Search for structures modified during the last month."
                   id="lastmsearchlink">Last Month</button>
            </div>
        </div>
        <div class="col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text">CCDC number</span>
                <input type="text" class="form-control" id="ccdc_num_adv">
            </div>
        </div>
    </div>

    <div class="row mb-2">
        <div class="col-xs-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text" data-bs-toggle="tooltip" title="should contain">Elements</span>
                <input type="text" class="form-control" placeholder="C H O ... (should contain)"
                       pattern="^[A-z]{1,}$" id="elements_in">
                <div class="form-check form-check-inline ms-2">
                    <input type="checkbox" class="form-check-input" id="onlythese_elem"
                           title="Only above Elements">
                    <label class="form-check-label" for="onlythese_elem">Only above</label>
                </div>
            </div>
        </div>
        <div class="col-xs-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text" data-bs-toggle="tooltip" title="should not contain">Elements</span>
                <input type="text" class="form-control" placeholder="C H O ... (should not contain)"
                       pattern="^[A-z]{1,}$" id="elements_out">
            </div>
        </div>
    </div>

    <div class="row mb-2">
        <div class="col-xs-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text" data-bs-toggle="tooltip" title="should contain">Text</span>
                <input type="text" class="form-control" placeholder="should contain" id="text_in">
            </div>
        </div>
        <div class="col-xs-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text" data-bs-toggle="tooltip" title="should not contain">Text</span>
                <input type="text" class="form-control" placeholder="should not contain" id="text_out">
            </div>
        </div>
    </div>

    <div class="row mb-2">
        <div class="col-12">
            <button type="button" class="btn btn-sm btn-success" id="advsearch-button" style="min-width:90px">
                Search
            </button>
        </div>
    </div>

</div>

<!-- End of advanced search -->
