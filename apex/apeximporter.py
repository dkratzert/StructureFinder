"""

https://stackoverflow.com/questions/12475850/how-can-an-sql-query-return-data-from-multiple-tables

By Robert Burrow:

CREATE OR REPLACE FUNCTION replace_return(p varchar) RETURNS varchar AS $$
  SELECT regexp_replace($1,'\\u000a','\n','g')
$$ LANGUAGE SQL;
CREATE OR REPLACE FUNCTION decode_url_part(p varchar) RETURNS varchar AS $$
SELECT convert_from(CAST(E'\\x' || array_to_string(ARRAY(
    SELECT CASE WHEN length(r.m[1]) = 1 THEN encode(convert_to(r.m[1], 'SQL_ASCII'), 'hex') ELSE substring(r.m[1] from 2 for 2) END
    FROM regexp_matches(substring($1 from 2), '%[0-9a-f][0-9a-f]|.', 'gi') AS r(m)
), '') AS bytea), 'UTF8');
$$ LANGUAGE SQL IMMUTABLE STRICT;

SELECT DISTINCT scd.samples.samples_id,
common.users.login_name as "Login",
common.groups.group_name as "Group",
scd.samples.last_modified as "Last Modified",
scd.samples.when_created as "When Created",
scd.samples.sample_name as "Sample Name",
decode_url_part(scd.samples.compound) as "Compound",
scd.samples.formula as "Formula", scd.struct_soln.form as "Formula Solution",
replace_return(decode_url_part(scd.samples.notes)) as "Notes",
ca.appearance as "Appearance",
ci.intensity as " Intensity",
cc1.color as "Color 1",
cc2.color as "Color 2",
decode_url_part(scd.samples.shape) as "Shape",
to_char(scd.sample_size.dimension_1, 'FM0D999') as "Size Min",
to_char(scd.sample_size.dimension_2, 'FM0D999') as "Size Mid",
to_char(scd.sample_size.dimension_3, 'FM0D999') as "Size Max",
count(scd.lsq_refinement.lsq_refinement_id) as "Cells Found",
lr.bravais_lattice_type as "Bravais Lattice",
to_char(lr.a, 'FM9990D0000') as "a",
to_char(lr.b, 'FM9990D0000') as "b",
to_char(lr.c, 'FM9990D0000') as "c",
to_char(lr.alpha, 'FM990D000') as "alpha",
to_char(lr.beta, 'FM990D000') as "beta",
to_char(lr.gamma, 'FM990D000') as "gamma",
scd.saint.integrate_nframes as "Frames",
scd.struct_soln.total_reflections as "Total Reflection",
scd.struct_soln.unique_reflections as "Unique Reflections",
scd.struct_soln.method as "Solution Method",
scd.struct_soln.rint as "Rint",
scd.struct_soln.rsig as "Rsig"
FROM scd.samples
LEFT JOIN scd.axscale ON scd.samples.samples_id=scd.axscale.samples_id
LEFT JOIN scd.lsq_refinement ON scd.samples.samples_id=scd.lsq_refinement.samples_id
LEFT JOIN scd.saint ON scd.samples.samples_id=scd.saint.samples_id
LEFT JOIN scd.struct_soln ON scd.samples.samples_id=scd.struct_soln.samples_id
LEFT JOIN scd.sample_size ON scd.samples.samples_id=scd.sample_size.samples_id
LEFT JOIN scd.sample_color ON scd.samples.samples_id=scd.sample_color.samples_id
JOIN (SELECT samples_id,appearance from scd.sample_color JOIN scd.crystal_appearances
ON scd.sample_color.crystal_appearances_id=scd.crystal_appearances.crystal_appearances_id) ca
ON (scd.samples.samples_id=ca.samples_id)
JOIN (SELECT samples_id,intensity from scd.sample_color JOIN scd.crystal_intensities
ON scd.sample_color.crystal_intensities_id=scd.crystal_intensities.crystal_intensities_id) ci
ON (scd.samples.samples_id=ci.samples_id)
JOIN (SELECT samples_id,color from scd.sample_color JOIN scd.crystal_colors
ON scd.sample_color.crystal_colors_id_1=scd.crystal_colors.crystal_colors_id) cc1
ON (scd.samples.samples_id=cc1.samples_id)
JOIN (SELECT samples_id,color from scd.sample_color JOIN scd.crystal_colors
ON scd.sample_color.crystal_colors_id_2=scd.crystal_colors.crystal_colors_id) cc2
ON (scd.samples.samples_id=cc2.samples_id)
JOIN (SELECT * from scd.lsq_refinement JOIN scd.bravais_lattice_types
ON scd.lsq_refinement.bravais_lattice_types_id=scd.bravais_lattice_types.bravais_lattice_types_id) lr
ON (scd.samples.samples_id=lr.samples_id)
LEFT JOIN common.users on scd.samples.users_id = common.users.users_id
LEFT JOIN common.groups on scd.samples.groups_id = common.groups.groups_id
WHERE scd.samples.revision = 1
GROUP BY scd.samples.sample_name, scd.samples.samples_id, scd.samples.compound, scd.samples.notes,
scd.samples.formula,scd.samples.shape,scd.samples.last_modified, scd.samples.when_created,
scd.samples.show_sample, scd.axscale.total_reflections,scd.saint.integrate_nframes,
struct_soln.form,struct_soln.total_reflections,struct_soln.unique_reflections,scd.struct_soln.method,
common.users.login_name,common.groups.group_name,scd.struct_soln.rint,scd.struct_soln.rsig,
scd.sample_size.dimension_1,scd.sample_size.dimension_2,scd.sample_size.dimension_3,
cc1.color,cc2.color,ca.appearance,ci.intensity,
lr.bravais_lattice_type,lr.a,lr.b,lr.c,lr.alpha,lr.beta,lr.gamma
ORDER BY samples_id;


-APEXdb: Als user bruker: psql -U bruker -f /Users/Shared/dkdumpall.sql BAXSdb
         Eventuell geht das auch als user daniel, aber mit -U bruker

"""
import pprint
import pg8000


class ApexDB():
    def __init__(self):
        self.conn = None
        self.cursor = None

    def initialize_db(self):
        """
        Initializes the database connection and cursor.
        """
        try:
            self.conn = pg8000.connect(user="BrukerPostgreSQL", password="Bruker-PostgreSQ",
                                       ssl=False, database="BAXSdb")
        except pg8000.core.ProgrammingError:
            self.conn = None
            return False
        self.cursor = self.conn.cursor()
        return True

    def get_all_data(self):
        """
        Fetches the relevant data from the APEX database.
        Does APEX2 also work?
        """
        self.cursor.execute("""SELECT 
                        lsq.samples_id,         --0  
                        lsq.a,                  --1
                        lsq.b,                  --2
                        lsq.c,                  --3
                        lsq.alpha,              --4
                        lsq.beta,               --5
                        lsq.gamma,              --6
                        sam.formula,               --7
                        sam.sample_name,           --8
                        sam.last_modified,         --9
                        sam.last_directory,        --10 Not the dir where the files are?
                        sam.compound,              --11
                        indx.first_image,           --12 First image of indexing
                        lsq.wavelength,              --13
                        col.crystal_colors_id_1,      --14 Farbe 1
                        col.crystal_colors_id_2,      --15 Farbe 2
                        ssi.dimension_1,              --16
                        ssi.dimension_2,              --17
                        ssi.dimension_3,              --18
                        sol.observed_reflections,     --19
                        sol.per_cent_observed,        --20
                        sol.rint,                     --21
                        sol.rsig,                     --22
                        sol.total_reflections,        --23
                        sol.unique_reflections,       --24
                        sol.form,                      --25
                        sol.per_cent_in_shell         --26
                        FROM scd.lsq_refinement AS lsq
                          INNER JOIN scd.samples AS sam 
                        ON lsq.samples_id=sam.samples_id
                          INNER JOIN scd.indexing AS indx
                        ON lsq.samples_id=indx.samples_id
                          INNER JOIN scd.sample_color AS col 
                        ON lsq.samples_id=col.samples_id
                          INNER JOIN scd.sample_size AS ssi 
                        ON lsq.samples_id=ssi.samples_id
                        INNER JOIN scd.struct_soln AS sol 
                        ON lsq.samples_id=sol.samples_id
                        
                        ;
                """)
        return self.cursor.fetchall()



if __name__ == '__main__':
    apex = ApexDB()
    conn = apex.initialize_db()
    if conn:
        data = apex.get_residuals(2)
        pprint.pprint(data)
        print('###############################')
        data = apex.get_all_data()
        pprint.pprint(data)


