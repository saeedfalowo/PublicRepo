-- CREATE a view to consolidate the raw barclays statement table with description split into multiple rows
drop view if exists statement.barclays_vw;
create or replace view statement.barclays_vw as
    with dated_tbl as (
        select id, nullif(date, '') as date, description from statement.barclays_raw
        where nullif(date, '') is not null
    ), dated_fully_tbl as (
        select
            raw.id,
            case
                when nullif(raw.date, '') is not null then date
                when nullif(raw.date, '') is null then (select d.date from dated_tbl d where d.id < raw.id order by d.id desc limit 1)
                else null
            end as date,
            description, money_out, money_in, balance, file_path, time_inserted
        from statement.barclays_raw raw
    ), agg_description_tbl as (
        select date, string_agg(description, ' ') as description_agg
        from  dated_fully_tbl
        group by date
    )
    select raw.id, raw.date, a.description_agg, raw.money_out, raw.money_in, raw.balance, raw.file_path, raw.time_inserted
    from statement.barclays_raw raw
    left join agg_description_tbl a on raw.date = a.date
    where raw.id in (select id from dated_tbl)
    order by raw.id
;