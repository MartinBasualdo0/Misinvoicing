proc sql;
create table work.fueguina as
select distinct
a.fech_aaaa,
a.fech_mm,
a.ccod_capi||a.ccod_part||a.ccod_subp||a.cnomen as nomen,
d.cdescri_red,
a.porg,
c.cdescri,
a.cuit,
b.crazon_social,
sum(a.val_dol) as cif,
sum(a.pnet) as pnet



from secexh.ce_tm3a a

left join secexh.ce_empresa b
on a.cuit=b.ccuit_empre
left join secexh.ce_pais c
on a.porg=c.ccod_pais
left join secexh.ce_cenice_enmienda d
on ((a.ccod_capi||a.ccod_part||a.ccod_subp||a.cnomen) = (d.ccod_capi||d.ccod_part||d.ccod_subp||d.cnomen)
and a.cnro_enmienda = d.cnro_enmienda)

where a.cuit='30711892520'
and a.fech_aa >='22'

group by
a.fech_aaaa,
a.fech_mm,
a.ccod_capi||a.ccod_part||a.ccod_subp||a.cnomen,
d.cdescri_red,
a.porg,
c.cdescri,
a.cuit,
b.crazon_social



;quit;
