import re
import csv
import time


def validate_phone_number(input):
    phone_number = input["phone"]
    if not phone_number:
        return {
            "nCleanNumber": None,
            "nExtension": None,
            "nRegion": None,
            "nCountry": None,
            "nStatus": "Invalid",
            "nReason": "Missing Number",
            "nDetails": "Invalid - Missing Number",
        }

    # Make Lowercase, Remove Trailing Spaces & Double+ Spaces
    nCleanNumber = re.sub(r" +", " ", phone_number.lower().strip())

    if nCleanNumber.count("*") > 1:
        nCleanNumber = nCleanNumber.replace("*", "-", 2)
    nCleanNumber = re.sub(
        r" *(extension|x?ext\.|ext:|ext|xt|ex|x+|loc|wzr|\*|#) *", " x", nCleanNumber
    )
    nCleanNumber = nCleanNumber.replace("javascript:void(0);", "", 1)

    phone_parse = nCleanNumber.split("x")
    nCleanNumber = phone_parse[0].strip()

    if not nCleanNumber:
        return {
            "nCleanNumber": None,
            "nExtension": None,
            "nRegion": None,
            "nCountry": None,
            "nStatus": "Invalid",
            "nReason": "Too Short: 00 digits",
            "nDetails": "Invalid - Too Short: 00 digits",
        }

    if nCleanNumber.startswith("00"):
        nCleanNumber = nCleanNumber.replace("00", "+", 1)

    # Process +
    nCleanNumber = re.sub(r"\++ *", "+", nCleanNumber)

    # Process Extensions
    nExtension = None
    if len(phone_parse) > 1:
        nExtension = "x" + "x".join(phone_parse[1:])
        digits = re.sub(r"\D", "", nExtension)
        if not digits:
            nExtension = None
        else:
            nExtension = re.sub(r"[^\d x]", "", nExtension)
            nExtension = re.sub(r"x[ ]+", "", nExtension)

    if not nExtension:
        patterns = [
            (r"(\d{10}) \(?(\d+)\)?", 1, 2),  # DDDDDDDDDD (E+)
            (r"(\d{3}[-\.]\d{3}[-\.]\d{4}) \(?(\d+)\)?", 1, 2),  # DDD-DDD-DDDD (E+)
            (
                r"(\(\d{3}\)[-\. ]?\d{3}[-\. ]?\d{4}) -?\(?(\d+)\)?",
                1,
                2,
            ),  # (DDD) DDD-DDDD (E+)
        ]

        for pattern, g1, g2 in patterns:
            mEX = re.search(pattern, nCleanNumber)
            if mEX:
                if mEX.group(g1) and mEX.group(g2):
                    nCleanNumber = mEX.group(g1)
                    nExtension = "x" + mEX.group(g2)
                break

    # Invalid Check: All Same Digits
    digits = re.sub(r"\D", "", nCleanNumber)
    if digits and len(digits) > 1 and all(d == digits[0] for d in digits):
        return {
            "nCleanNumber": None,
            "nExtension": None,
            "nRegion": None,
            "nCountry": None,
            "nStatus": "Invalid",
            "nReason": "All Same Digits",
            "nDetails": "Invalid - All Same Digits",
        }
        # return None, None, None, None, "Invalid", "All Same Digits", "Invalid - All Same Digits"

    nStatus = "Invalid"
    nReason = None
    status_ad = ""  # Additional Details for Status

    nRegion = None
    nCountry = None
    clean_digits = None
    # US & CA Phone Numbers
    patterns = [
        (
            r"^(\+1|1)?[-\. ]?\(?(\d{3})\)?[-\. ]?(\d{3})[-\. ]?(\d{4})$",
            2,
            3,
            4,
        ),  # 10 Digit NSN
        (
            r"^\(?(\+1|1)?\)?[-\. ]?(\d{3})[-\. ]?(\d{3})[-\. ]?(\d{4})$",
            2,
            3,
            4,
        ),  # 10 Digit NSN
    ]

    # +1 North America Valid Area Codes
    areaCodes1 = [
        ("North America", "United States", "Alabama", r"(205|251|256|334|659|938)"),
        ("North America", "United States", "Alaska", r"(907)"),
        ("North America", "United States", "Arizona", r"(480|520|602|623|928)"),
        ("North America", "United States", "Arkansas", r"(327|479|501|870)"),
        (
            "North America",
            "United States",
            "California",
            r"(209|213|279|310|323|341|350|369|408|415|424|442|510|530|559|562|619|626|628|650|657|661|669|707|714|747|760|805|818|820|831|840|858|909|916|925|949|951)",
        ),
        ("North America", "United States", "Colorado", r"(303|719|720|970|983)"),
        ("North America", "United States", "Connecticut", r"(203|475|860|959)"),
        ("North America", "United States", "Delaware", r"(302)"),
        ("North America", "United States", "District of Columbia", r"(202|771)"),
        (
            "North America",
            "United States",
            "Florida",
            r"(239|305|321|324|352|386|407|448|561|645|656|689|727|728|754|772|786|813|850|863|904|941|954)",
        ),
        (
            "North America",
            "United States",
            "Georgia",
            r"(229|404|470|478|678|706|762|770|912|943)",
        ),
        ("North America", "United States", "Hawaii", r"(808)"),
        ("North America", "United States", "Idaho", r"(208|986)"),
        (
            "North America",
            "United States",
            "Illinois",
            r"(217|224|309|312|331|447|464|618|630|708|730|773|779|815|847|861|872)",
        ),
        (
            "North America",
            "United States",
            "Indiana",
            r"(219|260|317|463|574|765|812|930)",
        ),
        ("North America", "United States", "Iowa", r"(319|515|563|641|712)"),
        ("North America", "United States", "Kansas", r"(316|620|785|913)"),
        ("North America", "United States", "Kentucky", r"(270|364|502|606|859)"),
        ("North America", "United States", "Louisiana", r"(225|318|337|504|985)"),
        ("North America", "United States", "Maine", r"(207)"),
        ("North America", "United States", "Maryland", r"(227|240|301|410|443|667)"),
        (
            "North America",
            "United States",
            "Massachusetts",
            r"(339|351|413|508|617|774|781|857|978)",
        ),
        (
            "North America",
            "United States",
            "Michigan",
            r"(231|248|269|313|517|586|616|679|734|810|906|947|989)",
        ),
        (
            "North America",
            "United States",
            "Minnesota",
            r"(218|320|507|612|651|763|952)",
        ),
        ("North America", "United States", "Mississippi", r"(228|601|662|769)"),
        (
            "North America",
            "United States",
            "Missouri",
            r"(235|314|417|557|573|636|660|816|975)",
        ),
        ("North America", "United States", "Montana", r"(406)"),
        ("North America", "United States", "Nebraska", r"(308|402|531)"),
        ("North America", "United States", "Nevada", r"(702|725|775)"),
        ("North America", "United States", "New Hampshire", r"(603)"),
        (
            "North America",
            "United States",
            "New Jersey",
            r"(201|551|609|640|732|848|856|862|908|973)",
        ),
        ("North America", "United States", "New Mexico", r"(505|575)"),
        (
            "North America",
            "United States",
            "New York",
            r"(212|315|329|332|347|363|516|518|585|607|624|631|646|680|716|718|838|845|914|917|929|934)",
        ),
        (
            "North America",
            "United States",
            "North Carolina",
            r"(252|336|472|704|743|828|910|919|980|984)",
        ),
        ("North America", "United States", "North Dakota", r"(701)"),
        (
            "North America",
            "United States",
            "Ohio",
            r"(216|220|234|283|326|330|380|419|436|440|513|567|614|740|937)",
        ),
        ("North America", "United States", "Oklahoma", r"(405|539|572|580|918)"),
        ("North America", "United States", "Oregon", r"(458|503|541|971)"),
        (
            "North America",
            "United States",
            "Pennsylvania",
            r"(215|223|267|272|412|445|484|570|582|610|717|724|814|835|878)",
        ),
        ("North America", "United States", "Rhode Island", r"(401)"),
        (
            "North America",
            "United States",
            "South Carolina",
            r"(803|821|839|843|854|864)",
        ),
        ("North America", "United States", "South Dakota", r"(605)"),
        (
            "North America",
            "United States",
            "Tennessee",
            r"(423|615|629|731|865|901|931)",
        ),
        (
            "North America",
            "United States",
            "Texas",
            r"(210|214|254|281|325|346|361|409|430|432|469|512|682|713|726|737|806|817|830|832|903|915|936|940|945|956|972|979)",
        ),
        ("North America", "United States", "Utah", r"(385|435|801)"),
        ("North America", "United States", "Vermont", r"(802)"),
        (
            "North America",
            "United States",
            "Virginia",
            r"(276|434|540|571|686|703|757|804|826|948)",
        ),
        ("North America", "United States", "Washington", r"(206|253|360|425|509|564)"),
        ("North America", "United States", "West Virginia", r"(304|681)"),
        (
            "North America",
            "United States",
            "Wisconsin",
            r"(262|274|353|414|534|608|715|920)",
        ),
        ("North America", "United States", "Wyoming", r"(307)"),
        ("North America", "Canada", "Alberta", r"(368|403|587|780|825)"),
        ("North America", "Canada", "British Columbia", r"(236|250|257|604|672|778)"),
        ("North America", "Canada", "Manitoba", r"(204|431|584)"),
        ("North America", "Canada", "New Brunswick", r"(428|506)"),
        ("North America", "Canada", "Newfoundland and Labrador", r"(709|879)"),
        ("North America", "Canada", "Northwest Territories", r"(867)"),
        ("North America", "Canada", "Nova Scotia", r"(782|902)"),
        ("North America", "Canada", "Nunavut", r"(867)"),
        (
            "North America",
            "Canada",
            "Ontario",
            r"(226|249|289|343|365|382|387|416|437|519|548|613|647|683|705|742|753|807|905|942)",
        ),
        ("North America", "Canada", "Prince Edward Island", r"(782|902)"),
        (
            "North America",
            "Canada",
            "Quebec",
            r"(263|354|367|418|438|450|468|514|579|581|819|873)",
        ),
        ("North America", "Canada", "Saskatchewan", r"(306|474|639)"),
        ("North America", "Canada", "Yukon", r"(867)"),
        ("Caribbean", "Anguilla", "Anguilla", r"(264)"),
        ("Caribbean", "Antigua and Barbuda", "Antigua and Barbuda", r"(268)"),
        ("Caribbean", "The Bahamas", "The Bahamas", r"(242)"),
        ("Caribbean", "Barbados", "Barbados", r"(246)"),
        ("Caribbean", "Bermuda", "Bermuda", r"(441)"),
        ("Caribbean", "British Virgin Islands", "British Virgin Islands", r"(284)"),
        ("Caribbean", "Cayman Islands", "Cayman Islands", r"(345)"),
        ("Caribbean", "Dominica", "Dominica", r"(767)"),
        ("Caribbean", "Dominican Republic", "Dominican Republic", r"(809|829|849)"),
        ("Caribbean", "Grenada", "Grenada", r"(473)"),
        ("Caribbean", "Jamaica", "Jamaica", r"(658|876)"),
        ("Caribbean", "Montserrat", "Montserrat", r"(664)"),
        ("Caribbean", "Puerto Rico", "Puerto Rico", r"(787|939)"),
        ("Caribbean", "Saint Kitts and Nevis", "Saint Kitts and Nevis", r"(869)"),
        ("Caribbean", "Saint Lucia", "Saint Lucia", r"(758)"),
        (
            "Caribbean",
            "Saint Vincent and the Grenadines",
            "Saint Vincent and the Grenadines",
            r"(784)",
        ),
        ("Caribbean", "Sint Maarten", "Sint Maarten", r"(721)"),
        ("Caribbean", "Trinidad and Tobago", "Trinidad and Tobago", r"(868)"),
        ("Caribbean", "Turks and Caicos Islands", "Turks and Caicos Islands", r"(649)"),
        ("Caribbean", "U.S. Virgin Islands", "U.S. Virgin Islands", r"(340)"),
        ("U.S. Pacific Territory", "American Samoa", "American Samoa", r"(684)"),
        ("U.S. Pacific Territory", "Guam", "Guam", r"(671)"),
        (
            "U.S. Pacific Territory",
            "Northern Mariana Islands",
            "Northern Mariana Islands",
            r"(670)",
        ),
        (
            "North America",
            "Canada",
            "Canada Special Services",
            r"(600|622|633|644|655|677|688)",
        ),
        (
            "North America",
            "Non Geographic",
            "Interexchange Carrier-Specific Services",
            r"(700)",
        ),
        (
            "North America",
            "Non Geographic",
            "Personal Communications Services",
            r"(500|521|522|523|524|525|526|527|528|529|532|533|535|538|542|543|544|545|546|547|549|550|552|553|554|556|566|558|569|577|578|588|589)",
        ),
        ("North America", "Non Geographic", "Premium Call Services", r"(900)"),
        (
            "North America",
            "Non Geographic",
            "Toll-Free",
            r"(800|822|833|844|855|866|877|880|881|882|883|884|885|886|887|888|889)",
        ),
        ("North America", "United States", "US Government", r"(710)"),
    ]

    for pattern, g2, g3, g4 in patterns:
        mUS = re.search(pattern, nCleanNumber)
        if mUS:
            if mUS.group(g2) and mUS.group(g3) and mUS.group(g4):
                nStatus = "Likely Not Valid"
                # nRegion = "North America"
                # nCountry = "US/CA"
                temp = "Unfamiliar Area Code: " + mUS.group(g2)
                # nCleanNumber = "+1 (" + mUS.group(g2) + ") " + mUS.group(g3) + "-" + mUS.group(g4)
                for iRegion, iCountry, location, areaCode in areaCodes1:
                    mUS2 = re.search(areaCode, mUS.group(g2))
                    if mUS2:
                        nStatus = "Valid"
                        nRegion = iRegion
                        nCountry = iCountry
                        temp = location + " Area Code: " + mUS.group(g2)
                        nCleanNumber = (
                            "+1 ("
                            + mUS.group(g2)
                            + ") "
                            + mUS.group(g3)
                            + "-"
                            + mUS.group(g4)
                        )
                        break
                status_ad += "" if temp == "" else " - " + temp
                nReason = temp
            break

    # UK Phone Numbers
    uk_nCleanNumber = re.sub(r"\D", "", nCleanNumber).strip()

    # General pattern for UK numbers
    uk_number_pattern = r"^(?:44|0|440)"

    # Patterns for specific types of UK numbers
    patterns = [
        r"1\d{9}",  # 10 Digit NSN
        r"2\d{9}",  # 10 Digit NSN
        r"3\d{9}",  # 10 Digit NSN
        r"7\d{9}",  # 10 Digit NSN
        r"8\d{9}",  # 10 Digit NSN
        r"9\d{9}",  # 10 Digit NSN
        r"55\d{8}",  # 10 Digit NSN
        r"56\d{8}",  # 10 Digit NSN
        r"1\d{8}",  # 9 Digit NSN
        r"800\d{6}",  # 9 Digit NSN
    ]

    uk_pattern = uk_number_pattern + "(" + "|".join(patterns) + ")$"
    mUK = re.match(uk_pattern, uk_nCleanNumber)
    if mUK:
        if mUK.group(1):
            nStatus = "Valid"
            nRegion = "Europe"
            nCountry = "United Kingdom"
            clean_digits = "{:02}".format(len(mUK.group(1))) + " digits"
            nReason = "Fits United Kingdom 9-10 NSN: " + clean_digits
            nCleanNumber = "+44 " + mUK.group(1)

    temp_number = None

    if not nCountry and nStatus != "Likely Not Valid":
        nCleanNumber = re.sub(r"[^\+\d]", " ", nCleanNumber)
        nCleanNumber = re.sub(r" +", " ", nCleanNumber).strip()

        patterns = [
            ("1", "North America | US/CA", 10, 10),
            ("7", "Asia | Russia/Kazakhstan", 10, 10),
            ("20", "Africa | Egypt", 8, 9),
            ("27", "Africa | South Africa", 9, 9),
            ("30", "Europe | Greece", 10, 10),
            ("31", "Europe | Netherlands", 9, 10),
            ("32", "Europe | Belgium", 9, 9),
            ("33", "Europe | France", 9, 9),
            ("34", "Europe | Spain", 9, 9),
            ("36", "Europe | Hungary", 9, 9),
            ("39", "Europe | Italy", 9, 10),
            ("40", "Europe | Romania", 9, 9),
            ("41", "Europe | Switzerland", 9, 9),
            ("43", "Europe | Austria", 9, 9),
            ("44", "Europe | United Kingdom", 9, 10),
            ("45", "Europe | Denmark", 8, 8),
            ("46", "Europe | Sweden", 9, 9),
            ("47", "Europe | Norway", 8, 8),
            ("48", "Europe | Poland", 9, 9),
            ("49", "Europe | Germany", 10, 11),
            ("51", "South America | Peru", 9, 9),
            ("52", "North America | Mexico", 10, 10),
            ("53", "Caribbean | Cuba", 8, 8),
            ("54", "South America | Argentina", 10, 10),
            ("55", "South America | Brazil", 10, 11),
            ("56", "South America | Chile", 9, 9),
            ("57", "South America | Colombia", 10, 10),
            ("58", "South America | Venezuela", 10, 10),
            ("60", "Asia | Malaysia", 9, 9),
            ("61", "Oceania | Australia", 9, 10),
            ("62", "Asia | Indonesia", 10, 11),
            ("63", "Asia | Philippines", 10, 10),
            ("64", "Oceania | New Zealand", 8, 10),
            ("65", "Asia | Singapore", 8, 8),
            ("66", "Asia | Thailand", 9, 9),
            ("81", "Asia | Japan", 10, 10),
            ("82", "Asia | South Korea", 9, 12),
            ("84", "Asia | Vietnam", 9, 10),
            ("86", "Asia | China", 11, 11),
            ("90", "Europe | Turkey", 10, 10),
            ("91", "Asia | India", 10, 10),
            ("92", "Asia | Pakistan", 10, 10),
            ("93", "Middle East | Afghanistan", 9, 9),
            ("94", "Asia | Sri Lanka", 9, 9),
            ("95", "Asia | Myanmar", 8, 10),
            ("98", "Asia | Iran", 10, 10),
            ("211", "Africa | South Sudan", 9, 9),
            ("212", "Africa | Morocco", 9, 9),
            ("213", "Africa | Algeria", 9, 9),
            ("216", "Africa | Tunisia", 8, 8),
            ("218", "Africa | Libya", 9, 9),
            ("220", "Africa | Gambia", 7, 7),
            ("221", "Africa | Senegal", 9, 9),
            ("222", "Africa | Mauritania", 8, 8),
            ("223", "Africa | Mali", 8, 8),
            ("224", "Africa | Guinea", 8, 8),
            ("225", "Africa | Ivory Coast", 8, 8),
            ("226", "Africa | Burkina Faso", 8, 8),
            ("227", "Africa | Niger", 8, 8),
            ("228", "Africa | Togo", 8, 8),
            ("229", "Africa | Benin", 8, 8),
            ("230", "Africa | Mauritius", 7, 7),
            ("231", "Africa | Liberia", 7, 8),
            ("232", "Africa | Sierra Leone", 8, 8),
            ("233", "Africa | Ghana", 9, 9),
            ("234", "Africa | Nigeria", 7, 10),
            ("235", "Africa | Chad", 8, 8),
            ("236", "Africa | Central African Republic", 8, 8),
            ("237", "Africa | Cameroon", 8, 9),
            ("238", "Africa | Cape Verde", 7, 7),
            ("239", "Africa | Sao Tome and Principe", 7, 7),
            ("240", "Africa | Equatorial Guinea", 9, 9),
            ("241", "Africa | Gabon", 8, 8),
            ("242", "Africa | Republic of the Congo", 9, 9),
            ("243", "Africa | Democratic Republic of the Congo", 9, 9),
            ("244", "Africa | Angola", 9, 9),
            ("245", "Africa | Guinea-Bissau", 7, 7),
            ("246", "Asia | British Indian Ocean Territory", 7, 7),
            ("247", "Africa | Ascension Island", 4, 4),
            ("254", "Africa | Kenya", 9, 9),
            ("255", "Africa | Tanzania", 9, 9),
            ("256", "Africa | Uganda", 9, 9),
            ("267", "Africa | Botswana", 7, 9),
            ("298", "Europe | Faroe Islands", 6, 6),
            ("299", "North America | Greenland", 6, 6),
            ("350", "Europe | Gibraltar", 8, 8),
            ("351", "Europe | Portugal", 9, 9),
            ("352", "Europe | Luxembourg", 6, 9),
            ("353", "Europe | Ireland", 7, 9),
            ("355", "Europe | Albania", 9, 9),
            ("356", "Europe | Malta", 8, 8),
            ("357", "Europe | Cyprus", 8, 8),
            ("358", "Europe | Finland", 5, 12),
            ("359", "Europe | Bulgaria", 7, 9),
            ("360", "Europe | Vatican City", 4, 4),
            ("370", "Europe | Lithuania", 8, 8),
            ("371", "Europe | Latvia", 8, 8),
            ("372", "Europe | Estonia", 7, 7),
            ("373", "Europe | Moldova", 8, 8),
            ("374", "Asia | Armenia", 8, 8),
            ("375", "Europe | Belarus", 9, 9),
            ("377", "Europe | Monaco", 6, 9),
            ("378", "Europe | San Marino", 6, 9),
            ("380", "Europe | Ukraine", 9, 9),
            ("381", "Europe | Serbia", 6, 9),
            ("382", "Europe | Montenegro", 6, 9),
            ("385", "Europe | Croatia", 7, 9),
            ("386", "Europe | Slovenia", 8, 8),
            ("387", "Europe | Bosnia and Herzegovina", 8, 8),
            ("389", "Europe | North Macedonia", 8, 8),
            ("421", "Europe | Slovakia", 9, 9),
            ("423", "Europe | Liechtenstein", 7, 7),
            ("500", "South America | Falkland Islands", 5, 5),
            ("501", "Central America | Belize", 7, 7),
            ("502", "Central America | Guatemala", 8, 8),
            ("503", "Central America | El Salvador", 8, 8),
            ("504", "Central America | Honduras", 8, 8),
            ("505", "Central America | Nicaragua", 8, 8),
            ("506", "Central America | Costa Rica", 8, 8),
            ("507", "Central America | Panama", 8, 8),
            ("508", "North America | Saint Pierre and Miquelon", 6, 6),
            ("509", "Caribbean | Haiti", 8, 8),
            ("590", "North America | Guadeloupe", 9, 9),
            ("591", "South America | Bolivia", 8, 8),
            ("593", "South America | Ecuador", 9, 9),
            ("594", "South America | French Guiana", 9, 9),
            ("595", "South America | Paraguay", 9, 9),
            ("597", "South America | Suriname", 6, 7),
            ("599", "North America | Caribbean Netherlands", 7, 7),
            ("670", "Asia | East Timor", 7, 8),
            ("672", "Oceania | Norfolk Island", 5, 5),
            ("673", "Asia | Brunei", 7, 7),
            ("675", "Oceania | Papua New Guinea", 7, 7),
            ("676", "Oceania | Tonga", 5, 5),
            ("677", "Oceania | Solomon Islands", 5, 5),
            ("678", "Oceania | Vanuatu", 5, 5),
            ("679", "Oceania | Fiji", 7, 7),
            ("680", "Oceania | Palau", 7, 7),
            ("681", "Oceania | Wallis and Futuna", 6, 6),
            ("682", "Oceania | Cook Islands", 5, 5),
            ("683", "Oceania | Niue", 4, 4),
            ("685", "Oceania | Samoa", 7, 7),
            ("686", "Oceania | Kiribati", 5, 5),
            ("687", "Oceania | New Caledonia", 6, 6),
            ("688", "Oceania | Tuvalu", 5, 5),
            ("689", "Oceania | French Polynesia", 6, 6),
            ("690", "Oceania | Tokelau", 4, 4),
            ("691", "Oceania | Micronesia", 7, 7),
            ("692", "Oceania | Marshall Islands", 7, 7),
            ("852", "Asia | Hong Kong", 8, 8),
            ("853", "Asia | Macau", 8, 8),
            ("855", "Asia | Cambodia", 9, 9),
            ("856", "Asia | Laos", 9, 9),
            ("870", "Oceania | Pitcairn Islands", 6, 6),
            ("880", "Asia | Bangladesh", 10, 10),
            ("886", "Asia | Taiwan", 9, 9),
            ("961", "Middle East | Lebanon", 8, 8),
            ("962", "Middle East | Jordan", 9, 9),
            ("963", "Middle East | Syria", 9, 9),
            ("964", "Middle East | Iraq", 10, 10),
            ("965", "Middle East | Kuwait", 8, 8),
            ("966", "Middle East | Saudi Arabia", 9, 9),
            ("967", "Middle East | Yemen", 9, 9),
            ("968", "Middle East | Oman", 8, 8),
            ("970", "Middle East | Palestine", 9, 9),
            ("971", "Middle East | United Arab Emirates", 9, 9),
            ("972", "Middle East | Israel", 7, 9),
            ("973", "Middle East | Bahrain", 8, 8),
            ("974", "Middle East | Qatar", 8, 8),
            ("975", "Asia | Bhutan", 8, 8),
            ("976", "Asia | Mongolia", 8, 8),
            ("977", "Asia | Nepal", 8, 10),
            ("992", "Asia | Tajikistan", 9, 9),
            ("993", "Asia | Turkmenistan", 8, 8),
            ("994", "Asia | Azerbaijan", 9, 9),
            ("995", "Asia | Georgia", 9, 9),
            ("996", "Asia | Kyrgyzstan", 9, 9),
            ("998", "Asia | Uzbekistan", 9, 9),
        ]

        for country_code, country_region, nsnMin, nsnMax in reversed(
            patterns
        ):  # Start with Longer Country Codes
            if nCleanNumber.startswith(
                "+" + country_code
            ):  # If there is a +, high chance it is a country code
                nRegion, nCountry = country_region.split(" | ")
                index = len(country_code) + 1
                if index < len(nCleanNumber) and nCleanNumber[index] == " ":
                    nsnTemp = nCleanNumber.replace("+" + country_code + " ", "", 1)
                else:
                    nsnTemp = nCleanNumber.replace("+" + country_code, "", 1)
                numCount = len(re.findall(r"\d", nsnTemp))
                if numCount >= nsnMin and numCount <= nsnMax:
                    nCleanNumber = "+" + country_code + " " + nsnTemp
                    clean_digits = "{:02}".format(numCount) + " digits"
                    nStatus = "Maybe Valid"
                    nReason = f"Fits {nCountry} {nsnMin}-{nsnMax} NSN: {clean_digits}"
                    break
                else:
                    temp_number = "+" + country_code + " " + nsnTemp
                    # if phone_number == "+36012312312": print(nCleanNumber)
                    clean_digits = "{:02}".format(numCount) + " digits"
                    nStatus = "Likely Not Valid"
                    nReason = (
                        f"Outside {nCountry} {nsnMin}-{nsnMax} NSN: {clean_digits}"
                    )
            elif nCleanNumber.startswith(country_code + " 0 "):
                nRegion, nCountry = country_region.split(" | ")
                nsnTemp = nCleanNumber.replace(country_code + " 0 ", "", 1)
                numCount = len(re.findall(r"\d", nsnTemp))
                if numCount >= nsnMin and numCount <= nsnMax:
                    nCleanNumber = "+" + country_code + " " + nsnTemp
                    clean_digits = "{:02}".format(numCount) + " digits"
                    nStatus = "Maybe Valid"
                    nReason = f"Fits {nCountry} {nsnMin}-{nsnMax} NSN: {clean_digits}"
                    break
                else:
                    temp_number = "+" + country_code + " " + nsnTemp
                    clean_digits = "{:02}".format(numCount) + " digits"
                    nStatus = "Likely Not Valid"
                    nReason = (
                        f"Outside {nCountry} {nsnMin}-{nsnMax} NSN: {clean_digits}"
                    )
            elif nCleanNumber.startswith(country_code + " "):
                nRegion, nCountry = country_region.split(" | ")
                nsnTemp = nCleanNumber.replace(country_code + " ", "", 1)
                numCount = len(re.findall(r"\d", nsnTemp))
                if numCount >= nsnMin and numCount <= nsnMax:
                    nCleanNumber = "+" + nCleanNumber
                    clean_digits = "{:02}".format(numCount) + " digits"
                    nStatus = "Maybe Valid"
                    nReason = f"Fits {nCountry} {nsnMin}-{nsnMax} NSN: {clean_digits}"
                    break
                else:
                    temp_number = "+" + country_code + " " + nsnTemp
                    clean_digits = "{:02}".format(numCount) + " digits"
                    nStatus = "Likely Not Valid"
                    nReason = (
                        f"Outside {nCountry} {nsnMin}-{nsnMax} NSN: {clean_digits}"
                    )
            elif nCleanNumber.startswith(country_code):
                nsnTemp = nCleanNumber.replace(country_code, "", 1)
                numCount = len(re.findall(r"\d", nsnTemp))
                if numCount >= nsnMin and numCount <= nsnMax:
                    nRegion, nCountry = country_region.split(" | ")
                    nCleanNumber = "+" + country_code + " " + nsnTemp
                    clean_digits = "{:02}".format(numCount) + " digits"
                    nStatus = "Maybe Valid"
                    nReason = f"Fits {nCountry} {nsnMin}-{nsnMax} NSN: {clean_digits}"
                    break

    if nReason and temp_number and nReason.startswith("Outside"):
        nCleanNumber = temp_number

    # One last country check based on digit length & area code matching
    if nStatus in ["Likely Not Valid", "Invalid"]:
        nsnTemp = re.sub(r"\D", "", nCleanNumber)
        numCount = len(nsnTemp)
        if numCount == 10:
            if int(nsnTemp[0]) == 0:
                nStatus = "Maybe Valid"
                if int(nsnTemp[1]) in [1, 5, 6, 9]:
                    nRegion = "Europe"
                    nCountry = "France"
                    nReason = "Looks like France: 10 NSN & Starts With " + nsnTemp[:2]
                    nCleanNumber = "+33 " + nsnTemp[1:10]
                else:
                    nRegion = None
                    nCountry = None
                    nReason = (
                        "Can Be Either UK, FR, or AU: 10 NSN & Starts With "
                        + nsnTemp[:2]
                    )
            else:
                for iRegion, iCountry, location, areaCode in areaCodes1:
                    mX = re.search(areaCode, nsnTemp[:3])
                    if mX:
                        nStatus = "Valid"
                        status_ad += "" if location == "" else " - " + location
                        nRegion = iRegion
                        nCountry = iCountry
                        nCleanNumber = (
                            "+1 ("
                            + nsnTemp[:3]
                            + ") "
                            + nsnTemp[3:6]
                            + "-"
                            + nsnTemp[6:10]
                        )
                        nReason = location + " Area Code: " + nsnTemp[:3]
                        break

    if nStatus == "Invalid":
        numCount = len(re.findall(r"\d", nCleanNumber))
        if numCount == 0:
            nReason = "Missing Digits"
        elif numCount < 9:
            nReason = "Too Short: " + "{:02}".format(numCount) + " digits"
        elif numCount > 15:
            nReason = "Too Long: " + "{:02}".format(numCount) + " digits"
        else:
            nStatus = "Likely Not Valid"
            nReason = "No Country Match: " + "{:02}".format(numCount) + " digits"

    last_six_digits = digits[-6:] if len(digits) >= 6 else digits
    if (
        nStatus in ["Valid", "Maybe Valid"]
        and len(digits) >= 6
        and all(d == last_six_digits[0] for d in last_six_digits)
    ):
        nStatus = "Likely Not Valid"
        nReason = f"Too Many {last_six_digits[0]}s"

    if "Toll-Free" in status_ad and nStatus in ["Valid"]:
        nStatus = "Maybe Valid"

    nDetails = nStatus

    nCountry = "United States" if nCountry in ["Non Geographic", "US/CA"] else nCountry
    if nCountry:
        nDetails += f" - {nRegion} | {nCountry}"

    nDetails += " - " + nReason

    if nExtension:
        nDetails += " - Has Extension"

    return {
        "nCleanNumber": nCleanNumber,
        "nExtension": nExtension,
        "nRegion": nRegion,
        "nCountry": nCountry,
        "nStatus": nStatus,
        "nReason": nReason,
        "nDetails": nDetails,
    }


def standardize_header(header):
    clean_header = re.sub(r"[\W]", " ", header).lower().strip()
    clean_header = re.sub(r" +", "_", clean_header)

    if clean_header in ("phone", "phone_number", "phones", "lead_phone"):
        return "phone"

    return header


if __name__ == "__main__":
    # input_file = 'natalie_phone_test.csv'   #Natalie's Phone Test
    # input_file = 'david_phone_test.csv'     #David's Phone Test
    # input_file = 'International Leads Routing Checkv2.csv' #Natalie's Original File
    # input_file = 'Historical DSA Webleads.csv'   #DSA Test
    input_file = "DFR MQL 2023.csv"  # DFR Test

    input_file = "./Test/" + input_file

    lowquality = (
        False  # Make it really easy to just get a clean list of low quality records
    )

    if lowquality:
        output_file = input_file.replace(".csv", "_lowquality.csv", 1)
    else:
        output_file = input_file.replace(".csv", "_results.csv", 1)

    with open(
        input_file, encoding="utf-8-sig", mode="r", errors="replace"
    ) as infile, open(output_file, mode="w", newline="") as outfile:
        tStart = time.time()  # Record the start time

        reader = csv.DictReader(infile)
        original_header = reader.fieldnames
        new_header = [h for h in original_header if h != ""]
        if not lowquality:
            new_header += [
                "nCleanNumber",
                "nExtension",
                "nRegion",
                "nCountry",
                "nStatus",
                "nReason",
                "nDetails",
                "cUS/CA",
            ]

        # Mapping to find the phone column
        hDict = {}
        for h in original_header:
            hDict[standardize_header(h)] = h

        # print(f"{new_header}")

        writer = csv.DictWriter(
            outfile,
            fieldnames=new_header,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()

        # Track Summary
        cTotal = 0
        cExtension = 0
        cCountry = 0
        cStatus_Valid = 0
        cStatus_MaybeValid = 0
        cStatus_LikelyNotValid = 0
        cStatus_Invalid = 0

        for original_row in reader:
            phone_number = (
                original_row[hDict.get("phone")] if hDict.get("phone") else None
            )
            nCleanNumber, nExtension, nRegion, nCountry, nStatus, nReason, nDetails = (
                validate_phone_number({"phone": phone_number}).values()
            )

            new_row = {k: v for k, v in original_row.items() if k}
            if lowquality:
                if nStatus in ["Likely Not Valid", "Invalid"] or nCountry not in [
                    "United States",
                    "Canada",
                ]:
                    writer.writerow(new_row)
            else:
                new_row.update(
                    {
                        "nCleanNumber": nCleanNumber,
                        "nExtension": nExtension,
                        "nRegion": nRegion,
                        "nCountry": nCountry,
                        "nStatus": nStatus,
                        "nReason": nReason,
                        "nDetails": nDetails,
                        "cUS/CA": nCountry
                        if nCountry in ["United States", "Canada"]
                        else "Other",
                    }
                )
                writer.writerow(new_row)

            cTotal += 1
            if nExtension:
                cExtension += 1
            if nCountry:
                cCountry += 1

            if nStatus == "Valid":
                cStatus_Valid += 1
            elif nStatus == "Maybe Valid":
                cStatus_MaybeValid += 1
            elif nStatus == "Likely Not Valid":
                cStatus_LikelyNotValid += 1
            elif nStatus == "Invalid":
                cStatus_Invalid += 1

        tEnd = time.time()  # Record the end time
        tDuration = round(tEnd - tStart, 1)  # Calculate the Duration
        print(f"# Execution Time:    {tDuration}s")
        print(f"# Total:             {format(cTotal,',')}")
        print(
            f"# w/ Extension:      {format(cExtension,',')} | {str(round(cExtension / cTotal * 100,1))}%"
        )
        print(
            f"# w/ Country:        {format(cCountry,',')} | {str(round(cCountry / cTotal * 100,1))}%"
        )
        print(
            f"# Phone Valid:       {format(cStatus_Valid,',')} | {str(round(cStatus_Valid / cTotal * 100,1))}%"
        )
        print(
            f"# Phone Maybe Valid: {format(cStatus_MaybeValid,',')} | {str(round(cStatus_MaybeValid / cTotal * 100,1))}%"
        )
        print(
            f"# Phone LikelyNot V: {format(cStatus_LikelyNotValid,',')} | {str(round(cStatus_LikelyNotValid / cTotal * 100,1))}%"
        )
        print(
            f"# Phone Invalid:     {format(cStatus_Invalid,',')} | {str(round(cStatus_Invalid / cTotal * 100,1))}%"
        )

    # Unit Tests
    failure = None
    unitTests = [
        (
            "nDetails",
            "732-579-2122",
            "Valid - North America | United States - New Jersey Area Code: 732",
        ),
        (
            "nDetails",
            "(732) 579-2122",
            "Valid - North America | United States - New Jersey Area Code: 732",
        ),
        (
            "nDetails",
            "8882732200 (1337)",
            "Maybe Valid - North America | United States - Toll-Free Area Code: 888 - Has Extension",
        ),
        (
            "nDetails",
            "510-245-4300 2112",
            "Valid - North America | United States - California Area Code: 510 - Has Extension",
        ),
        (
            "nDetails",
            "(650)231-1300 -121",
            "Valid - North America | United States - California Area Code: 650 - Has Extension",
        ),
        (
            "nDetails",
            "(570)824-1000  349",
            "Valid - North America | United States - Pennsylvania Area Code: 570 - Has Extension",
        ),
        ("nCleanNumber", "001 4128997378", "+1 (412) 899-7378"),
        ("nCleanNumber", "+61413993344  Im in Australia so please", "+61 413993344"),
        (
            "nDetails",
            "+43 (0) 50607",
            "Likely Not Valid - Europe | Austria - Outside Austria 9-9 NSN: 06 digits",
        ),
        (
            "nDetails",
            "Click to dial(856) 728-8234",
            "Valid - North America | United States - New Jersey Area Code: 856",
        ),
        ("nCleanNumber", "Click to dial(856) 728-8234", "+1 (856) 728-8234"),
        ("nCleanNumber", "7159864777GK", "+1 (715) 986-4777"),
        ("nCleanNumber", "33 (0) 170371426", "+33 170371426"),
        ("nCleanNumber", "(+1) 5194323550", "+1 (519) 432-3550"),
        ("nReason", "+91 98204 51173", "Fits India 10-10 NSN: 10 digits"),
        ("nCleanNumber", "201*238*8265 2", "+1 (201) 238-8265"),
        ("nCleanNumber", "8585521587*1314", "+1 (858) 552-1587"),
        (
            "nDetails",
            "(242_ 424-5336",
            "Valid - Caribbean | The Bahamas - The Bahamas Area Code: 242",
        ),
        (
            "nDetails",
            "+36012312312",
            "Maybe Valid - Europe | Hungary - Fits Hungary 9-9 NSN: 09 digits",
        ),
        ("nCleanNumber", "+36012312312", "+36 012312312"),
        (
            "nDetails",
            "+3601234",
            "Maybe Valid - Europe | Vatican City - Fits Vatican City 4-4 NSN: 04 digits",
        ),
        ("nCleanNumber", "+3601234", "+360 1234"),
        ("nCleanNumber", "09173659565", "+44 9173659565"),
        ("nCountry", "0662082024", "France"),
        ("nCleanNumber", "0662082024", "+33 662082024"),
        ("nCleanNumber", "12234567", "12234567"),
        ("nCleanNumber", "9205922000", "+1 (920) 592-2000"),
        ("nDetails", "**********", "Invalid - Missing Digits"),
        ("nExtension", "7325792122 x22 x x32", "x22 x32"),
        ("nExtension", "636-778-2925 x.304", "x304"),
        ("nCountry", "+44723819176", "United Kingdom"),
        ("nStatus", "+1 1231231234", "Likely Not Valid"),
        ("nStatus", "1", "Invalid"),
        # ("+155 333 59783", 0, "+1 (553) 335-9783"),
    ]

    for i, (index, test, rExpected) in enumerate(unitTests):
        result = validate_phone_number({"phone": test})
        rActual = result[index]
        if rActual != rExpected:
            failure = True
            print(f"T{i} phone_number: {test}")
            print(f"T{i} Expected->: {rExpected}")
            print(f"T{i} Actual--->: {rActual}")
            print(f"T{i} aCleanNumber: " + result["nCleanNumber"])
            print(f"T{i} aDetails:     " + result["nDetails"] + "\n")

    if not failure:
        print(f"SUCCESS: New File: {output_file}\n")
