
-- ==============================
-- v_active_interest_crops
-- ==============================
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_active_interest_crops` AS select `interest_whitelist`.`crop_id` AS `crop_id`,`interest_whitelist`.`display_name` AS `display_name` from `interest_whitelist` where (`interest_whitelist`.`is_active` = true) order by `interest_whitelist`.`sort_order`;



-- ==============================
-- view_crop_trade_daily
-- ==============================
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `view_crop_trade_daily` AS select `ft`.`trd_clcln_ymd` AS `trd_clcln_ymd`,`mcv`.`item_code` AS `item_code`,`mcv`.`gds_mclsf_nm` AS `gds_mclsf_nm`,`ft`.`crop_full_code` AS `crop_full_code`,`mcv`.`gds_sclsf_nm` AS `gds_sclsf_nm`,`ft`.`grade_label` AS `grd_cd`,`ft`.`grade_label` AS `grd_nm`,`ft`.`j_sanji_cd` AS `j_sanji_cd`,`mrs`.`j_sanji_nm` AS `j_sanji_nm`,`ft`.`unit_tot_qty` AS `unit_tot_qty`,(case when (`ft`.`unit_tot_qty` > 0) then (`ft`.`totprc` / `ft`.`unit_tot_qty`) else 0 end) AS `avg_price` from ((`fact_trade` `ft` join `master_crop_variety` `mcv` on((`ft`.`crop_full_code` = `mcv`.`crop_full_code`))) left join `map_region_weather_station` `mrs` on((`ft`.`j_sanji_cd` = `mrs`.`j_sanji_cd`)));


-- ==============================
-- vw_crop_item_name
-- ==============================
CREATE ALGORITHM=UNDEFINED DEFINER=`jikfarm1`@`%` SQL SECURITY DEFINER VIEW `vw_crop_item_name` AS select distinct `master_crop_variety`.`item_code` AS `item_code`,`master_crop_variety`.`gds_mclsf_nm` AS `gds_mclsf_nm` from `master_crop_variety`;


-- ==============================
-- vw_map_region_sanji
-- ==============================
CREATE ALGORITHM=UNDEFINED DEFINER=`jikfarm1`@`%` SQL SECURITY DEFINER VIEW `vw_map_region_sanji` AS select `map_region_weather_station`.`j_sanji_cd` AS `j_sanji_cd`,max(`map_region_weather_station`.`j_sanji_nm`) AS `j_sanji_nm` from `map_region_weather_station` group by `map_region_weather_station`.`j_sanji_cd`;
