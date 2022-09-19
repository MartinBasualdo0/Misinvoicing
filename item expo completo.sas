proc sql;
/*Esto es histório*/
create table work.expo1 as
select

a.fech_aaaa,
a.fech_mm,
a.CANIO,
a.ANA,
a.DEST,
a.REG,
a.CANIO||a.ANA||a.DEST||a.REG as docu,
a.sec,
a.pais,
a.cuit,
a.cnro_enmienda,
a.nomen,
a.sim,
a.pnet,
a.val_dol

from secexh.ce_tx3a a

where a.fech_aa between '21' and '22' 

;quit;

proc sql;
create table work.expo2 as
/*Producción*/
select

b.fcump,
b.canio,
b.ccod_ana,
b.ccod_dest,
b.cnro_doc,
b.canio||b.ccod_ana||b.ccod_dest||b.cnro_doc as docu

from secex.ce_cara_expo b
where b.canio between '19' and '22'

/*Es una trampita para buscar más rápido*/

;quit;

proc sql;
create table work.expo3 as
/*Producción e histórico*/
select b.*

from work.expo2 b
where b.docu in (select distinct a.docu from work.expo1 a)

;quit;

proc sql;
create table work.expo4 as
select 
put(day(datepart(b.fcump)),z2.) as dia,
put(month(datepart(b.fcump)),z2.) as mes,
put(year(datepart(b.fcump)),z4.) as anio,
a.*,
case
	when missing(c.ccod_asoc) then a.pais
	else c.ccod_asoc
	end as pdest_final

from expo1 a
left join expo3 b 
on(a.docu=b.docu)
left join secex.ce_pais c
	on (a.pais = c.ccod_pais)
/*Chequear que el left join no genere duplicados,
tiene q contener las mismas obs*/
;quit;

proc sql;
create table work.expo_doc_total as
/*Existen operaciones que nada más se distinguen por número de documento*/
select distinct
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
sum(a.val_dol) as fob,
sum(a.pnet) as pnet

from expo4 a
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
d.CDESCRI_RED, 
a.sim,
a.pdest_final,
b.cdescri
;quit;

PROC export data= work.expo_doc_total
DBMS=CSV
outfile = "/srv/sas/secex/home/mbasualdo/expo_doc_total.csv"
replace ;
;


/*data _null_;*/
/*    data _null_;*/
/*    fname="tempfile";*/
/*    rc=filename(fname,  "/srv/sas/secex/home/mbasualdo/fletes_impo_mt_uso_zona_&p_aniod._&p_anioh._1_&p_mes..xlsx.bak");*/
/*    if rc = 0 and fexist(fname) then*/
/*       rc=fdelete(fname);*/
/*    rc=filename(fname);*/
/*run;*/


