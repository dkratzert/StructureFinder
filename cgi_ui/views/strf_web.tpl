% rebase('cgi_ui/views/strf_base.tpl', title='StructureFinder')

<!-- "dropZone" adds drag&drop support for the web site -->
<div class="container" id="dropZone">
    <h2>StructureFinder</h2>


    <a type="button" class="btn btn-primary btn-sm" data-toggle="collapse" data-target="#adv-search"
       id="toggle_advsearch-button">Advanced Search</a>
    <a type="button" class="btn btn-warning btn-sm" id="all_structures">Show All</a>
    <a type="button" class="btn btn-default btn-sm {{!'' if host == '127.0.0.1' else 'invisible'}}"
       id="cellsearchcsd_button"
       href="http://{{my_ip}}/csd" target="_blank">CellCheckCSD</a>

    <!-- ------------  The collapsible for simple search options: -----------------  -->
    <div class="row" id="mainsearch">
        <div class="column col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-addon" data-toggle="tooltip" title="Search for a Unit Cell">Unit Cell</span>
                <input type="text" class="form-control"
                       placeholder="a  b  c  &alpha;  &beta;  &gamma;    (or drag&drop .p4p, .res, cif file)"
                       style="font-style: italic" id="smpl_cellsrch" name="cell">
                <div class="input-group-sm input-group-btn">
                    <button class="btn btn-default" type="submit" id="smpl_cellsrchbutton">
                        <i class="glyphicon glyphicon-search"></i>
                    </button>
                </div>
            </div>
        </div>
        <div class="column col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-addon" data-toggle="tooltip" title="Search for a Unit Cell">Text</span>
                <input type="text" class="form-control" placeholder="Search Text" id="smpl_textsrch" name="text">
                <div class="input-group-sm input-group-btn">
                    <button class="btn btn-default" type="submit" id="smpl_textsrchbutton">
                        <i class="glyphicon glyphicon-search"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ---------------------    End of simple search     ----------------------    -->


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
                    <input type="text" class="form-control form-sm" style="font-style: italic"
                           placeholder="a b c &alpha; &beta; &gamma;" id="cell_adv">
                </div>
            </div>
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
        </div>

        <div class="row">
            <div class="column col-xs-6">
                <div class="input-group input-group-sm input-group-prepend has-success">
                    <span class="input-group-addon" data-toggle="tooltip" title="should contain">Elements</span>
                    <input type="text" class="form-control form-sm" placeholder="C H O ... (should contain)"
                           pattern="^[A-z]{1,}$" id="elements_in">
                    <input class="checkbox-addon" type="checkbox" aria-label="Only these elements"
                           title="Only above Elements" id="onlythese_elem"> Only above Elements
                </div>
            </div>
            <div class="column col-xs-6">
                <div class="input-group input-group-sm has-error">
                    <span class="input-group-addon" data-toggle="tooltip" title="should not contain">Elements</span>
                    <input type="text" class="form-control form-sm" placeholder="C H O ... (should not contain)"
                           pattern="^[A-z]{1,}$" id="elements_out">
                </div>
            </div>
        </div>

        <div class="row">
            <div class="column col-xs-6">
                <div class="input-group input-group-sm has-success">
                    <span class="input-group-addon" data-toggle="tooltip" title="should contain">Text</span>
                    <input type="text" class="form-control form-sm" placeholder="should contain" id="text_in">
                </div>
            </div>
            <div class="column col-xs-6">
                <div class="input-group input-group-sm has-error">
                    <span class="input-group-addon" data-toggle="tooltip" title="should not contain">Text</span>
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
    <div class="row">
        <div class="column col-sm-12">
            <div id="mygrid" style="height: 450px"></div>
        </div>
    </div>

    <div class="row">
        <div class="column col-sm-12">
            <div class="panel panel-default">
                <div class="panel-body">
                    <span class="invisible btn-group" id="cellrow"> </span>
                    <span class="btn btn-default glyphicon glyphicon-copy invisible" id="cell_copy_btn"
                          data-toggle="tooltip" title="Copy cell to clipboard." data-clipboard-target="#hidden-cell">
                </span>
                    <span class="btn-group invisible" id="growCheckBoxgroup">
                        &nbsp;&nbsp;&nbsp;&nbsp;
                        <input type="checkbox" title="Grow Structure" value="false" id="growCheckBox">Grow Structure
                </span>
                </div>
            </div>
        </div>
    </div>

    <div id="all_residuals">

        <div class="row">
            <div class="column col-md-4 panel panel-default invisible" id="jsmolcolumn"
                 data-toggle="tooltip" title="Asymmetric Unit"></div>
            <div class="column col-md-4" id="residualstable1"></div>
            <div class="column col-md-4" id="residualstable2"></div>
        </div>


        <div class="row">
            <div class="col-sm-12">
                <span id="residuals"></span>
            </div>
        </div>
    </div>
    <address>
        <strong>
            <a href="https://www.xs3.uni-freiburg.de/research/structurefinder">StructureFinder</a>
            <span id="version"></span> by Daniel Kratzert
        </strong><br>
        <a href="mailto:daniel.kratzert@ac.uni-freiburg.de">daniel.kratzert@ac.uni-freiburg.de</a><br>
        <p><a href="http://{{my_ip}}/dbfile.sqlite" download="structurefinder.sqlite" type="application/*">Download
            database file</a></p>
    </address>

</div>  <!-- End of the main container div -->


