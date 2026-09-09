<!-- ------------  The collapsible for simple search options: -----------------  -->
    <div class="row" id="mainsearch">
        <div class="column col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text" data-bs-toggle="tooltip" title="Search for a Unit Cell">Unit Cell</span>
                <input type="text" class="form-control"
                       placeholder="a  b  c  &alpha;  &beta;  &gamma;    (or drag&drop .p4p, .res, cif file)"
                       style="font-style: italic" id="smpl_cellsrch" name="cell">
                <button class="btn btn-outline-secondary" type="submit" id="smpl_cellsrchbutton">
                    <i class="bi bi-search"></i>
                </button>
            </div>
        </div>
        <div class="column col-sm-6">
            <div class="input-group input-group-sm">
                <span class="input-group-text" data-bs-toggle="tooltip" title="Search for a Unit Cell">Text</span>
                <input type="text" class="form-control" placeholder="Search Text" id="smpl_textsrch" name="text">
                <button class="btn btn-outline-secondary" type="submit" id="smpl_textsrchbutton">
                    <i class="bi bi-search"></i>
                </button>
            </div>
        </div>
    </div>

    <!-- ---------------------    End of simple search     ----------------------    -->