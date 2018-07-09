from datetime import datetime, timedelta
from edgydata.backend.hybrid import Hybrid
from edgydata.visualize import chart

twodaysago = datetime.now() - timedelta(days=2)
now = datetime.now()
hdb = Hybrid(debug=True)
mine = hdb.get_power(start=twodaysago, end=now)
chart(mine)
