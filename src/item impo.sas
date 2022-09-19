%let p_nomen = 12019000;

proc sql;
/*Histórico*/
create table work.impo1 as 
select
a.fech_aaaa,
a.fech_mm,
a.CANIO,
a.ANA,
a.DEST,
a.REG,
a.CANIO||a.ANA||a.DEST||a.REG as docu,
a.sec,
a.porg as pais,
a.cuit,
a.cnro_enmienda,
a.nomen,
a.pnet,
a.val_dol as cif,
a.fob_dol as fob

from secexh.ce_tm3a a

where a.fech_aa between '21' and '22' 
/*Soja*/
and a.CCOD_CAPI= '12'
and a.CCOD_PART = '01'
and a.CCOD_SUBP = '90'
and a.CNOMEN = '00'
/*Trigo: 10019900*/
or (a.CCOD_CAPI= '10'
and a.CCOD_PART = '01'
and a.CCOD_SUBP = '99'
and a.CNOMEN = '00')
/*aceite soja: 15071000*/
or (a.CCOD_CAPI= '10'
and a.CCOD_PART = '05'
and a.CCOD_SUBP = '90'
and a.CNOMEN = '10')
/*pellets soja: 23040010*/
or (a.CCOD_CAPI= '23'
and a.CCOD_PART = '04'
and a.CCOD_SUBP = '00'
and a.CNOMEN = '10')
/*biodisel: 38260000*/
or (a.CCOD_CAPI= '38'
and a.CCOD_PART = '26'
and a.CCOD_SUBP = '00'
and a.CNOMEN = '00')
/*Maiz: 10059010*/
or (a.CCOD_CAPI= '10'
and a.CCOD_PART = '05'
and a.CCOD_SUBP = '90'
and a.CNOMEN = '10')

;quit;

proc sql;
create table work.impo2 as
/*Producción*/
SELECT 
t1.CANIO, 
t1.CCOD_ANA, 
t1.CCOD_DEST, 
t1.CNRO_DOC, 
t1.CANIO||t1.CCOD_ANA||t1.CCOD_DEST||t1.CNRO_DOC as docou,
t1.FINICIO
FROM SECEX.CE_CARA_IMPO t1
where t1.canio between '20' and '22'
;quit;

proc sql;
create table work.impo3 as
select t1.CANIO, 
          t1.CCOD_ANA, 
          t1.CCOD_DEST, 
          t1.CNRO_DOC, 
		  t1.docou as docu,
          year(datepart(t1.FINICIO)) as anio_ofic,
		  month(datepart(t1.FINICIO)) as mes_ofic,
		  day(datepart(t1.finicio)) as dia_ofic
 
 from work.impo2 t1

 where t1.docou in (select b.docu from work.impo1 b)

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
a.cnro_enmienda,
a.nomen, 
d.CDESCRI_RED as nomen_descri,
a.pdest_final as pais,
b.cdescri as pais_descri,
sum(a.cif) as cif,
sum(a.fob) as fob,
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
d.CDESCRI_RED, 
a.pdest_final,
b.cdescri
 ;quit;

