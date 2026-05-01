import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(f"""
    # The Coupon Effect: Quantifying Private School Subsidy with the Texas Vouchers

    When discussing the impact of school vouchers, the conversation often revolves around the total number of applications. But as Fort Worth parents, we need to ask a deeper question: **Are these vouchers "saving" students from underperforming public schools, or are they primarily subsidizing families who have already chosen private education or homeschooling?**

    By looking beyond the raw application numbers and calculating the Delta between Total Applications and Public Applications, we can reveal the true story. We call this the **Coupon Effect**.

    ### The Math
    **The Query**: `(Total Apps - Public Apps) / Total Apps`

    ### Why It Matters
    This metric identifies districts where the voucher is functioning more like a "tax coupon" for families already outside the public system.

    ### The Nerd Factor
    A high percentage here strongly suggests the program isn't rescuing students from public schools, but rather subsidizing existing private choices. Below, we dive into the data to compare this Coupon Effect against a proxy for the district's median household income (the percentage of students *not* economically disadvantaged).
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import altair as alt

    return alt, mo, pl


@app.cell
def _(pl):
    total_voucher_apps = pl.read_json('voucher-applications-by-isd.json')
    prev_pub_voucher_apps = pl.read_json('previous-public-school-applications.json')
    tapr_district_reference = pl.read_csv('2025 District Reference.csv', skip_lines=1)
    tapr_district_student = pl.read_csv('2025 District Student Information.csv', skip_lines=1)
    return (
        prev_pub_voucher_apps,
        tapr_district_reference,
        tapr_district_student,
        total_voucher_apps,
    )


@app.cell
def _(mo):
    mo.md(f"""
    ## Gathering the Data

    To answer this, we need to combine two main data sources:
    1. **Texas Voucher Application Data**: The total number of voucher applications and the subset from families whose children were previously enrolled in a Texas public school.
    2. **Texas Academic Performance Reports (TAPR) Data**: Specifically, the 2024-2025 student information, which provides us with total enrollments and the counts of economically disadvantaged students per district.

    We calculate the `pct_not_econ_disadv` metric to proxy median household income for the district. The higher this percentage, the generally wealthier the district.
    """)
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _(pl, tapr_district_reference, tapr_district_student):
    tapr_student_selected = tapr_district_student.select(
        'DISTRICT', 'DPETALLC', 'DPETSPEC', 'DPETECOC', 'DPETNEDC' 
    )

    tapr_district_data = tapr_district_reference.select(
        'DISTRICT', 'DISTNAME', 'DFLCHART', 'D_RATING', 'OUTCOME', 'COUNTY'
    ).join(tapr_student_selected, on='DISTRICT').select(
        pl.col('DISTRICT').alias('district_number'),
        pl.col('COUNTY').alias('county_number'),
        pl.col('DISTNAME').alias('district_name'),
        pl.col('DFLCHART').alias('charter_flag'),
        pl.col('D_RATING').alias('district_overall_grade'),
        pl.col('OUTCOME').alias('district_spec_ed_status'),
        pl.col('DPETALLC').alias('all_student_count'),
        pl.col('DPETSPEC').alias('spec_ed_count'),
        pl.col('DPETECOC').alias('econ_disadv_count'),
        pl.col('DPETNEDC').alias('not_econ_disadv_count'),
    ).with_columns(
        pct_not_econ_disadv=pl.col('not_econ_disadv_count') / pl.col('all_student_count')
    )
    return (tapr_district_data,)


@app.cell
def _(tapr_district_data):
    print(tapr_district_data.schema)
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _(prev_pub_voucher_apps, total_voucher_apps):
    print("Total Apps:", len(total_voucher_apps))
    print("Prev Pub Apps:", len(prev_pub_voucher_apps))
    return


@app.cell
def _(pl, prev_pub_voucher_apps, total_voucher_apps):
    coupon_tbl = total_voucher_apps.join(other=prev_pub_voucher_apps, on='district', how='left').rename({
        "applications_submitted_right": "previous_public_applications"
    }).with_columns(
        pl.col('previous_public_applications').fill_null(0)
    ).with_columns(
        coupon_applications=pl.col('applications_submitted') - pl.col('previous_public_applications')
    ).with_columns(
        coupon_rate=pl.col('coupon_applications') / pl.col('applications_submitted')
    )
    return (coupon_tbl,)


@app.cell
def _(coupon_tbl):
    print(coupon_tbl.columns)
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _(coupon_tbl, pl, tapr_district_data):
    _analysis_tbl_part1 = coupon_tbl.join(tapr_district_data, left_on='district', right_on='district_name')

    _analysis_tbl_part2 = coupon_tbl.join(_analysis_tbl_part1, left_on='district', right_on='district', how='anti').filter(
        pl.col('district_number') != ""
    ).with_columns(
        pl.col('district_number').cast(pl.Int64)
    ).join(
        tapr_district_data, on='district_number'
    )

    common_cols = [
        'district_number', 'district', 'county_number', 'applications_submitted', 'previous_public_applications', 
        'coupon_applications', 'coupon_rate', 'charter_flag', 'district_overall_grade', 
        'district_spec_ed_status', 'all_student_count', 'spec_ed_count', 'econ_disadv_count', 
        'not_econ_disadv_count', 'pct_not_econ_disadv'
    ]

    analysis_tbl = pl.concat(
        [
            _analysis_tbl_part1.with_columns(pl.col("district_number_right").cast(pl.String).alias("district_number")).select(common_cols),
            _analysis_tbl_part2.with_columns(pl.col("district_number").cast(pl.String)).select(common_cols),
        ],
        how="vertical"
    )
    return (analysis_tbl,)


@app.cell
def _():
    print(_analysis_tbl_part1.columns)
    print(_analysis_tbl_part2.columns)
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _():
    # deleted
    return


@app.cell
def _(mo):
    mo.md(f"""
    ## Side Quest: The Outliers
    Before looking at the broader trend, a couple of extreme outliers in our data deserve a spotlight: **Roscoe Collegiate** and the **Harmony** charter school network.

    When you join the TAPR demographic data with the voucher applications, these districts exhibit strange and out-sized behaviors. Below is a quick look at their raw numbers. Notice how massive the application volume is relative to the student population or typical application rates.
    """)
    return


@app.cell
def _(analysis_tbl, mo, pl):
    outliers_df = analysis_tbl.filter(pl.col('district').str.contains('(?i)roscoe|harmony'))
    mo.ui.table(outliers_df.select([
        'district', 'applications_submitted', 'coupon_applications', 'coupon_rate', 
        'all_student_count', 'district_overall_grade', 'charter_flag'
    ]), selection=None)
    return (outliers_df,)


@app.cell
def _(mo):
    mo.md(f"""
    ### A Tale of Two Districts
    When we peel back the layers on these two extreme outliers, an incredible narrative emerges.

    First, consider **Roscoe Collegiate**. This is a massive district serving over 12,000 students. Unfortunately, it struggles—carrying an overall **"F" rating**. For many families in this area, it is the only game in town. Yet despite the massive student body and the failing grade, only 93 families applied for a voucher. Here, the "Coupon Effect" is lower (~34%), indicating that a handful of brave souls are trying to exit a failing system, joining the small baseline of families already seeking alternative education.

    Then, there is **Harmony ISD**. On the surface, things look perfectly fine—it holds a solid **"B" rating**. But look closer at the sheer volume of applications. Harmony is a tiny district with a total enrollment of just 895 students. Yet somehow, **320 applications** were submitted for vouchers. That means over a third of the *entire student body* applied to leave a supposedly "good" school district. It suggests a staggering mass exodus and raises serious questions about what is happening beneath the surface of that "B" rating.

    These exceptional outliers tell a fascinating story about how the voucher is being used at the fringes—either as a rare escape hatch in massive struggling districts, or as a floodgate in surprisingly small ones.
    """)
    return


@app.cell(hide_code=True)
def _(alt, outliers_df, pl):
    # Create FIPS codes for our outliers
    # Texas FIPS prefix is 48. The county code is (county_number * 2) - 1 formatted to 3 digits.
    map_df = outliers_df.with_columns(
        fips=pl.lit("48") + ((pl.col('county_number') * 2) - 1).cast(pl.String).str.pad_start(3, '0')
    )

    # Fetch topojson via direct URL to avoid needing the vega_datasets python package
    counties_url = "https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/us-10m.json"
    counties = alt.topo_feature(counties_url, 'counties')

    tx_map = alt.Chart(counties).mark_geoshape(
        fill='#eee', stroke='white', strokeWidth=0.5
    ).transform_filter(
        "datum.id >= 48000 && datum.id < 49000" # Filter to Texas
    ).encode(
    ).properties(
        width=600, height=400,
        title="Geographic Context: Where are the Outliers?"
    )

    points = alt.Chart(counties).mark_geoshape(
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(map_df, 'fips', ['district', 'applications_submitted', 'coupon_rate'])
    ).transform_filter(
        "isValid(datum.district)"
    ).encode(
        color=alt.Color('district:N', legend=alt.Legend(title="Outlier District", orient='bottom')),
        tooltip=[
            alt.Tooltip('district:N', title='District'),
            alt.Tooltip('applications_submitted:Q', title='Total Applications'),
            alt.Tooltip('coupon_rate:Q', title='Coupon Effect', format='.1%')
        ]
    )

    tx_map + points
    return


@app.cell
def _(mo):
    mo.md(f"""
    ## Side Quest: Liberating the Data

    I'd be remiss if I didn't mention *how* we had to get this data. The original voucher application numbers were released in a deeply frustrating format: a static PDF with un-aligned columns, missing district IDs, and district names that didn't perfectly match the official TAPR reporting names.

    In my opinion, publishing public data in a clickable PDF is as good as not releasing it at all. Whether it's a symptom of intentional obfuscation or sheer negligence in the talent appointed to the task, it's unacceptable.

    We believe data belongs to the public, and you shouldn't have to be a data engineer to hold programs accountable. So, we've done the dirty work of parsing, cleaning, and joining the voucher applications with the official TAPR identifiers. You can explore or download the cleaned dataset right here.
    """)
    return


@app.cell
def _(analysis_tbl, mo):
    mo.vstack([
        mo.download(
            data=analysis_tbl.write_csv().encode('utf-8'),
            filename='cleaned_voucher_and_tapr_data.csv',
            mimetype='text/csv',
            label='⬇️ Download Cleaned Data (CSV)'
        ),
        mo.ui.dataframe(analysis_tbl)
    ])
    return


@app.cell
def _(alt, analysis_tbl, pl):
    # Prepare data for charting
    # We remove the extreme outliers (Roscoe and Harmony) to better visualize the main cluster of districts
    chart_df = analysis_tbl.filter(
        ~pl.col('district').str.contains('(?i)roscoe|harmony')
    ).with_columns(
        is_fw=(pl.col('district').str.contains('(?i)fort worth|tarrant'))
    ).drop_nulls(['pct_not_econ_disadv', 'coupon_rate'])

    # Create a scatter plot comparing wealth proxy vs coupon effect
    scatter = alt.Chart(chart_df).mark_circle(opacity=0.7).encode(
        x=alt.X('pct_not_econ_disadv:Q', 
                title='Pct Not Econ Disadvantaged (Wealth Proxy)',
                axis=alt.Axis(format='%')),
        y=alt.Y('coupon_rate:Q', 
                title='Coupon Effect Rate',
                axis=alt.Axis(format='%'),
                scale=alt.Scale(domain=[.4,1])),
        size=alt.Size('applications_submitted:Q', title='Total Applications', scale=alt.Scale(range=[20, 1000])),
        color=alt.Color('is_fw:N', 
                        scale=alt.Scale(domain=[True, False], range=['#d95f02', '#1b9e77']),
                        legend=alt.Legend(title='FW / Tarrant Area')),
        tooltip=[
            alt.Tooltip('district:N', title='District'),
            alt.Tooltip('coupon_rate:Q', title='Coupon Rate', format='.1%'),
            alt.Tooltip('pct_not_econ_disadv:Q', title='Not Econ Disadv (%)', format='.1%'),
            alt.Tooltip('applications_submitted:Q', title='Total Apps'),
            alt.Tooltip('coupon_applications:Q', title='Coupon Apps')
        ]
    ).properties(
        title='The Coupon Effect vs. District Wealth (Proxy)',
        width=700,
        height=500
    ).interactive()

    scatter
    return


@app.cell
def _(mo):
    mo.md(f"""
    ### What is the data telling us?
    With the extreme outliers removed, the true picture emerges. If these vouchers were genuinely a "lifeline" specifically for lower-income families seeking to exit underperforming public schools, we would expect to see a strong diagonal relationship here—poorer districts (lower on the wealth proxy X-axis) utilizing the vouchers aggressively, with less utilization in wealthier districts.

    **But that's not what the graph shows.**
    Instead, we see a broad, horizontal cloud of points spanning the entire wealth spectrum. The "Coupon Effect" is uniformly high across the board, frequently sitting above 50% regardless of a district's median household income. This is powerful evidence that the voucher is functioning exactly as we suspected: primarily as a subsidy—a "tax coupon"—for a massive segment of families who were already opting out of the public school system anyway.
    """)
    return


if __name__ == "__main__":
    app.run()
