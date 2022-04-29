<!-- The collapsible for Advanced search options: -->
<div id="adv-search" class="collapse">
    <div class="row">
        <div class="column col-sm-12">
            <div class="btn-group btn-group-sm" role="group">
                <a href="#" class="badge" id="more_info_badge">info</a>
                <span>&nbsp;&nbsp;</span>
                <input title="More cell search results" class="checkbox-addon" type="checkbox"
                       value="" id="more_results">More cell search results
                <span>&nbsp;&nbsp;</span>
                <input title="Find supercells" type="checkbox" class="checkbox-addon-sm"
                       value="" id="supercells">Find supercells
                <span>&nbsp;&nbsp;</span>
                %include('cgi_ui/views/spgr.tpl')
                Find by space group
            </div>
        </div>
    </div>

    <div id="more-cell-info" class="collapse">
        <div class="row">
            <div class="col-sm-6">
                <b>regular</b><br>
                volume: &plusmn;3 %, length: 0.06&nbsp;&angst;, angle: 1.0&deg;<br>
                <br>
                <b>more results option</b><br>
                volume: &plusmn;9 &percnt;, length: 0.2&nbsp;&angst;, angle: 2.0&deg;<br>
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

    <div class="row">
        <div class="column col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-addon">Uni Cell</span>
                <label for="cell_adv"></label>
                <input type="text" class="form-control form-sm" placeholder="a b c &alpha; &beta; &gamma;"
                       id="cell_adv">
            </div>
        </div>

        <div class="column col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-addon"><i>R</i><sub>1</sub> <=</span>
                <label for="r1_val_adv"></label>
                <input type="text" class="form-control form-sm" id="r1_val_adv">
                <span class="input-group-addon">%</span>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="column col-sm-6">
            <div class="input-group input-group-sm w2ui-field">
                <span class="input-group-addon" data-toggle="tooltip"
                      title="Search for structures that were modified between two dates">Date from</span>
                <input class="input-sm" title="Date" type="text" id="date1" style="width: 95%">
                <span class="input-group-addon">to</span>
                <input class="input-sm" title="Date" type="text" id="date2" style="width: 95%">
                <a type="button" class="input-group-addon"
                   data-toggle="tooltip" title="Search for structures modified during the last month."
                   id="lastmsearchlink"> From Last Month</a>
            </div>
        </div>
        <div class="column col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-addon">CCDC number</span>
                <label for="ccdc_num_adv"></label>
                <input type="text" class="form-control form-sm" id="ccdc_num_adv">
            </div>
        </div>
    </div>

    <div class="row">
        <div class="column col-xs-6">
            <div class="input-group input-group-sm input-group-prepend has-success">
                <span class="input-group-addon" data-toggle="tooltip" title="should contain">Elements</span>
                <label for="elements_in"></label>
                <input type="text" class="form-control form-sm" placeholder="C H O ... (should contain)"
                       pattern="^[A-z]{1,}$" id="elements_in">
                <input class="checkbox-addon" type="checkbox" aria-label="Only these elements"
                       title="Only above Elements" id="onlythese_elem"> Only above Elements
            </div>
        </div>
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-error">
                <span class="input-group-addon" data-toggle="tooltip" title="should not contain">Elements</span>
                <label for="elements_out"></label>
                <input type="text" class="form-control form-sm" placeholder="C H O ... (should not contain)"
                       pattern="^[A-z]{1,}$" id="elements_out">
            </div>
        </div>
    </div>

    <div class="row">
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-success">
                <span class="input-group-addon" data-toggle="tooltip" title="should contain">Text</span>
                <label for="text_in"></label>
                <input type="text" class="form-control form-sm" placeholder="should contain" id="text_in">
            </div>
        </div>
        <div class="column col-xs-6">
            <div class="input-group input-group-sm has-error">
                <span class="input-group-addon" data-toggle="tooltip" title="should not contain">Text</span>
                <label for="text_out"></label>
                <input type="text" class="form-control form-sm" placeholder="should not contain" id="text_out">
            </div>
        </div>
    </div>

    <div class="row">
        <div class="column col-xs-12">
            <a type="button" class="btn btn-sm btn-success" id="advsearch-button" style="min-width:90px">
                Search </a>
        </div>
    </div>

    <br>
</div>

<!-- End of collapsible for search options. -->