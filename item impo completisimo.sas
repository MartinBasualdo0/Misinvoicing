%let p_nomen = 12019000;

proc sql;
/*Histórico*/
create table work.impo1 as 
select
/*a.fech_aaaa,*/
/*a.fech_mm,*/
/*a.CANIO,*/
/*a.ANA,*/
/*a.DEST,*/
/*a.REG,*/
a.CANIO||a.ANA||a.DEST||a.REG||a.DIGMARIA as docu,
a.sec,
a.porg as pais,
a.cuit,
a.cnro_enmienda,
a.nomen,
a.sim,
a.pnet,
a.val_dol as cif
/*a.fob_dol as fob*/

from secexh.ce_tm3a a

where a.fech_aa between '21' and '22' 

;quit;

proc sql;
create table work.impo2 as
/*Producción*/
SELECT 
t1.CANIO, 
t1.CCOD_ANA, 
t1.CCOD_DEST, 
t1.CNRO_DOC, 
t1.cdig,
t1.canio||t1.ccod_ana||t1.ccod_dest||t1.cnro_doc||t1.cdig as docu,
t1.FINICIO

FROM SECEX.CE_CARA_IMPO t1
where t1.canio between '19' and '22'
;quit;

proc sql;
create table work.impo3 as
select 
/*t1.CANIO, */
/*          t1.CCOD_ANA, */
/*          t1.CCOD_DEST, */
/*          t1.CNRO_DOC, */
		  t1.docu as docu,
          year(datepart(t1.FINICIO)) as anio_ofic,
		  month(datepart(t1.FINICIO)) as mes_ofic,
		  day(datepart(t1.finicio)) as dia_ofic
 
 from work.impo2 t1

 where t1.docu in (select b.docu from work.impo1 b)

 ;quit;

proc sql;
create table work.impo4 as
select
put(b.anio_ofic,z4.) as anio,
put(b.mes_ofic,z2.) as mes,
put(b.dia_ofic,z2.) as dia,
a.*,
case
	when missing(c.ccod_asoc) then a.pais
	else c.ccod_asoc
	end as pdest_final

from impo1 a
left join impo3 b 
on(a.docu=b.docu)
left join secex.ce_pais c
	on (a.pais = c.ccod_pais)
/*Chequear que el left join no genere duplicados,
tiene q contener las mismas obs*/
;quit;

proc sql;
 create table work.impo_item as
select distinct
a.dia,
a.mes,
a.anio, 
a.cuit,
c.crazon_social as empresa,
a.cnro_enmienda as enmienda,
a.nomen as ncm, 
d.CDESCRI_RED as ncm_descri,
a.sim as sim,
a.pdest_final as pais,
b.cdescri as pais_descri,
sum(a.cif) as cif,
sum(a.pnet) as pnet

 
from work.impo4 a
left join secex.ce_pais b
	on (a.pdest_final=b.ccod_pais)

left join secexh.ce_empresa c
	on (a.cuit = c.ccuit_empre)

 left join SECEXH.CE_CENICE_ENMIENDA d
	on (a.cnro_enmienda = d.cnro_enmienda
	and a.nomen = d.ccod_capi||d.ccod_part||d.ccod_subp||d.cnomen)

group by
a.dia,
a.mes,
a.anio, 
a.cuit,
c.crazon_social,
a.cnro_enmienda,
a.nomen,
a.sim,
d.CDESCRI_RED, 
a.pdest_final,
b.cdescri
 ;quit;

proc sql;
create table work.impo_doc_completo as
/*Existen operaciones que nada más se distinguen por número de documento*/
select
a.dia,
a.mes,
a.anio, 
a.cuit as cuit,
c.crazon_social as empresa,
a.cnro_enmienda as enmienda,
a.nomen as ncm, 
d.CDESCRI_RED as ncm_descri,
a.sim as sim,
a.pdest_final as pais,
b.cdescri as pais_descri,
a.docu as docu,
a.sec as sec,
a.cif as cif,
a.pnet as pnet

from impo4 a
left join secex.ce_pais b
	on (a.pdest_final=b.ccod_pais)

left join secexh.ce_empresa c
	on (a.cuit = c.ccuit_empre)

 left join SECEXH.CE_CENICE_ENMIENDA d
	on (a.cnro_enmienda = d.cnro_enmienda
	and a.nomen = d.ccod_capi||d.ccod_part||d.ccod_subp||d.cnomen)

;quit;


 PROC export data= work.impo_doc_completo
DBMS=CSV
outfile = "/srv/sas/secex/home/mbasualdo/impo_doc_completo.csv"
replace ;
;

