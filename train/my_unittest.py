import unittest
import text_clean as tc


# Test text cleaning methods.

class Test_clean(unittest.TestCase):
    def test_cashtag1(self):
        checkstr = tc.remove_cashtag('Analysts See $0.31 EPS for CenterPoint Energy Inc. $CNP - https://t.co/NPuObzJS9E')
        outstr = 'Analysts See .31 EPS for CenterPoint Energy Inc.  - https://t.co/NPuObzJS9E'
        self.assertEqual(checkstr, outstr)

    def test_cashtag2(self): 
        checkstr = tc.remove_cashtag('Dividend Champions With 20% Stock Price Potential -&gt; https://t.co/KBFzpewsL6 - $ORI $DOV $NUE $ABM $ITW $GD $NC $PH $SWK $PNR $SEIC')
        outstr = 'Dividend Champions With 20% Stock Price Potential -&gt; https://t.co/KBFzpewsL6 -           '
        self.assertEqual(checkstr, outstr)

    def test_cashtag3(self):
        checkstr = tc.remove_cashtag('$0.31 EPS Expected for CenterPoint Energy Inc. $CNP https://t.co/hcWeeUsBL4')
        outstr =  '.31 EPS Expected for CenterPoint Energy Inc.  https://t.co/hcWeeUsBL4'
        self.assertEqual(checkstr, outstr)

    def test_cashtag4(self):
        checkstr = tc.remove_cashtag('$SEIC Advance Auto Parts $AAP PT Raised to $154 at RBC Capital; $10+ in EPS Power')
        outstr = ' Advance Auto Parts  PT Raised to  at RBC Capital; + in EPS Power'
        self.assertEqual(checkstr, outstr)

    def test_mention1(self):
        checkstr = tc.remove_mention('So when are we going to get @LEGO_Group models of @Tesla cars, @elonmusk?')
        outstr = 'So when are we going to get  models of  cars, ?'
        self.assertEqual(checkstr, outstr)

    def test_mention2(self):
        checkstr = tc.remove_mention('OKE new 52 week high of $71.78 $OKE https://t.co/Kul3gUQMP1 @benzinga')
        outstr = 'OKE new 52 week high of $71.78 $OKE https://t.co/Kul3gUQMP1 '
        self.assertEqual(checkstr, outstr)

    def test_mention3(self):
        checkstr = tc.remove_mention('Elon will Confirm that Tesla is Unstoppable before Battery Day - Heres ... via @YouTube')
        outstr = 'Elon will Confirm that Tesla is Unstoppable before Battery Day - Heres ... via '
        self.assertEqual(checkstr, outstr)

    def test_hashtag1(self):
        checkstr = tc.remove_hashtag('#LynnFinance Tesla plans battery manufacturing facility under project Roadrunner: document')
        outstr = ' Tesla plans battery manufacturing facility under project Roadrunner: document'
        self.assertEqual(checkstr, outstr)

    def test_hashtag2(self):
        checkstr = tc.remove_hashtag('Top Implied #Volatility Gainers $RCII $SWKS $TWTR $PVG $QCOM $HIG $DAL $TSCO $DVMT $ACAD $RF https://t.co/3rvsfTPuHO')
        outstr = 'Top Implied  Gainers $RCII $SWKS $TWTR $PVG $QCOM $HIG $DAL $TSCO $DVMT $ACAD $RF https://t.co/3rvsfTPuHO'
        self.assertEqual(checkstr, outstr)

    def test_count_cashtag1(self):
        ntags = tc.count_cashtags('@GerberKawasaki @elonmusk Is morning star valuation of $731 for $TSLA right? What about $TTD, $ROKU ?')
        self.assertEqual(ntags, 2)

    def test_count_cashtag2(self):
        ntags = tc.count_cashtags('$SEIC going to $14 $ORI $DOV $NUE $ABM $ITW $TSLAQ')
        self.assertEqual(ntags, 6)

    def test_normalize1(self):                
        checkstr = tc.normalize_doc('The lay-offs will affect 240 people out of the total 320 Okmetic employees in Finland .')
        outstr = 'lay off affect peopl out total okmet employe in finland'
        self.assertEqual(checkstr, outstr)
        
    def test_normalize2(self):                    
        checkstr = tc.normalize_doc('Short sale volume(not short interest) for  on 2018-07-11 is 66%.  45%  38%  55%  37%')
        outstr = 'short sale volum not short interest'
        self.assertEqual(checkstr, outstr)

    def test_normalize3(self):                    
        checkstr = tc.normalize_doc('West Oak Capital LLC Lifted Its Stake in Leucadia National Corp  by .64 Billion as Stock Value Declined')
        outstr = 'west oak capit llc lift stake in leucadia nation corp billion stock valu declin'
        self.assertEqual(checkstr, outstr)


if __name__ == '__main__':

    unittest.main(argv=[''])
