import numpy as np

__version__ = '0.0.1'


class DataFrame:

    def __init__(self, data):
        """
        A DataFrame holds two dimensional heterogeneous data. Create it by
        passing a dictionary of NumPy arrays to the values parameter

        Parameters
        ----------
        data: dict
            A dictionary of strings mapped to NumPy arrays. The key will
            become the column name.
        """
        # check for correct input types
        self._check_input_types(data)

        # check for equal array lengths
        self._check_array_lengths(data)

        # convert unicode arrays to object
        self._data = self._convert_unicode_to_object(data)

        # Allow for special methods for strings
        self.str = StringMethods(self)
        self._add_docs()

    def _check_input_types(self, data):
        if not isinstance(data, dict):
            raise TypeError("'data' must be a dictionary")
        for key,value in data.items():
            if not isinstance(key, str):
                raise TypeError("'key' must be string")
            if not isinstance(value, np.ndarray):
                raise TypeError("'value' must be a numpy array")
            if value.ndim > 1:
                raise ValueError("dimension of 'value' must be 1")


    def _check_array_lengths(self, data):
        for key,value in data.items():
            to_check = value.size
            break

        for key,value in data.items():
            if value.size != to_check:
                raise ValueError("All 'values' must be of the same length")


    def _convert_unicode_to_object(self, data):
        new_data = {}
        for col_name, values in data.items():
            if values.dtype.kind == 'U':
                new_data[col_name] = values.astype('O')
            else:
                new_data[col_name] = values
        return new_data

    def __len__(self):
        """
        Make the builtin len function work with our dataframe

        Returns
        -------
        int: the number of rows in the dataframe
        """
        for key, value in self._data.items():
        	return len(value)

    @property
    def columns(self):
        """
        _data holds column names mapped to arrays
        take advantage of internal ordering of dictionaries to
        put columns in correct order in list. Only works in 3.6+

        Returns
        -------
        list of column names
        """
        cols = []
        for key in self._data.keys():
        	cols.append(key)
        return cols


    @columns.setter
    def columns(self, columns):
        """
        Must supply a list of columns as strings the same length
        as the current DataFrame

        Parameters
        ----------
        columns: list of strings

        Returns
        -------
        None
        """
        if not isinstance(columns, list):
        	raise TypeError("'columns' must be a list")
        if len(self._data) != len(columns):
        	raise ValueError("Number of cols should be same as og dataframe")
        for c in columns:
        	if not isinstance(c, str):
        		raise TypeError("All column names must be strings")
        if len(set(columns)) != len(columns):
        	raise ValueError("Column names must be unique")


        i = 0
        temp = {}
        for key, value in self._data.items():
        	new_key = columns[i]
        	temp[new_key] = self._data[key]
        	i+=1

        self._data = temp

    @property
    def shape(self):
        """
        Returns
        -------
        two-item tuple of number of rows and columns
        """
        for key, value in self._data.items():
        	rows = len(value)
        	break
        cols = len(list(self._data))
        return tuple([rows, cols])

    def _repr_html_(self):
        """
        Used to create a string of HTML to nicely display the DataFrame
        in a Jupyter Notebook. Different string formatting is used for
        different data types.

        The structure of the HTML is as follows:
        <table>
            <thead>
                <tr>
                    <th>data</th>
                    ...
                    <th>data</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>{i}</strong></td>
                    <td>data</td>
                    ...
                    <td>data</td>
                </tr>
                ...
                <tr>
                    <td><strong>{i}</strong></td>
                    <td>data</td>
                    ...
                    <td>data</td>
                </tr>
            </tbody>
        </table>
        """
        html = '<table><thead><tr><th></th>'
        for col in self.columns:
            html += f"<th>{col:10}</th>"

        html += '</tr></thead>'
        html += "<tbody>"

        only_head = False
        num_head = 10
        num_tail = 10
        if len(self) <= 20:
            only_head = True
            num_head = len(self)

        for i in range(num_head):
            html += f'<tr><td><strong>{i}</strong></td>'
            for col, values in self._data.items():
                kind = values.dtype.kind
                if kind == 'f':
                    html += f'<td>{values[i]:10.3f}</td>'
                elif kind == 'b':
                    html += f'<td>{values[i]}</td>'
                elif kind == 'O':
                    v = values[i]
                    if v is None:
                        v = 'None'
                    html += f'<td>{v:10}</td>'
                else:
                    html += f'<td>{values[i]:10}</td>'
            html += '</tr>'

        if not only_head:
            html += '<tr><strong><td>...</td></strong>'
            for i in range(len(self.columns)):
                html += '<td>...</td>'
            html += '</tr>'
            for i in range(-num_tail, 0):
                html += f'<tr><td><strong>{len(self) + i}</strong></td>'
                for col, values in self._data.items():
                    kind = values.dtype.kind
                    if kind == 'f':
                        html += f'<td>{values[i]:10.3f}</td>'
                    elif kind == 'b':
                        html += f'<td>{values[i]}</td>'
                    elif kind == 'O':
                        v = values[i]
                        if v is None:
                            v = 'None'
                        html += f'<td>{v:10}</td>'
                    else:
                        html += f'<td>{values[i]:10}</td>'
                html += '</tr>'

        html += '</tbody></table>'
        return html

    @property
    def values(self):
        """
        Returns
        -------
        A single 2D NumPy array of the underlying data
        """
        vals = []
        for key, value in self._data.items():
            vals.append(value.reshape(len(value), 1))
        all_vals = np.column_stack(vals)
        return all_vals

    @property
    def dtypes(self):
        """
        Returns
        -------
        A two-column DataFrame of column names in one column and
        their data type in the other
        """
        type_mapping = {'O': 'string', 'i': 'int', 'f': 'float', 'b': 'bool'}
        DTYPE_NAME = {'Column Name': [], 'Data Type': []}
        for key, value in self._data.items():
            DTYPE_NAME['Column Name'].append(key)
            DTYPE_NAME['Data Type'].append(type_mapping[value.dtype.kind])

        DTYPE_NAME['Column Name'] = np.array(DTYPE_NAME['Column Name'])
        DTYPE_NAME['Data Type'] = np.array(DTYPE_NAME['Data Type'])

        return DataFrame(DTYPE_NAME)        


    def __getitem__(self, item):
        """
        Use the brackets operator to simultaneously select rows and columns
        A single string selects one column -> df['colname']
        A list of strings selects multiple columns -> df[['colname1', 'colname2']]
        A one column DataFrame of booleans that filters rows -> df[df_bool]
        Row and column selection simultaneously -> df[rs, cs]
            where cs and rs can be integers, slices, or a list of integers
            rs can also be a one-column boolean DataFrame

        Returns
        -------
        A subset of the original DataFrame
        """
        sub_dict = {}

        if isinstance(item, DataFrame):
            if len(item.columns) > 1:
                raise ValueError("cannot pass more than one column")
            else:
                key = item.columns[0]
                bools = item.values
                if bools.dtype.kind != 'b':
                    raise ValueError("df must be of type 'bool'")
                for i in range(0, len(bools)):
                    if bools[i][0]:
                        for key, value in self._data.items():
                            if key in sub_dict:
                                sub_dict[key].append(value[i])
                            else:
                                sub_dict[key] = []
                                sub_dict[key].append(value[i])
                            # print(value[i])
                    i = i + 1

                for key, value in sub_dict.items():
                    sub_dict[key] = np.array(sub_dict[key])

        elif isinstance(item, list):
            for i in item:
                col = i
                vals = self._data[i]
                sub_dict[col] = vals
        elif not isinstance(item, str):
            raise TypeError("'column name' must be a string")
        else:
            col = item
            vals = self._data[item]
            sub_dict[col] = vals 
        return DataFrame(sub_dict)


    def _getitem_tuple(self, item):
        # simultaneous selection of rows and cols -> df[rs, cs]
        pass

    def _ipython_key_completions_(self):
        # allows for tab completion when doing df['c
        return self.columns

    def __setitem__(self, key, value):
        # adds a new column or a overwrites an old column
        if not isinstance(key, str):
        	raise NotImplementedError("'df' can only set a single col")
        if isinstance(value, np.ndarray):
        	if value.ndim > 1:
        		raise ValueError("'value' should be a 1 dim array")
        	elif len(value) != len(self):
        		raise ValueError("'length mistmatch'")
        	else:
        		if value.dtype.kind == 'U':
        			value.astype('O')
        		self._data[key] = value

        elif isinstance(value, DataFrame):
        	if len(value.columns) > 1:
        		raise ValueError("'df can have only one column")
        	elif len(value) != len(self):
        		raise ValueError("'df' length mistmatch")
        	else:
        		self._data[key] = next(iter(value._data.values()))

        elif isinstance(value, (int, float, str, bool)):
        	self._data[key] = np.repeat(value, len(self))
        else: 
        	raise TypeError("invalid type for 'value'")
    def head(self, n=5):
        """
        Return the first n rows

        Parameters
        ----------
        n: int

        Returns
        -------
        DataFrame
        """
        head_dict = {}
        for key, value in self._data.items():
        	head_dict[key] = value[:n]


        return DataFrame(head_dict)

    def tail(self, n=5):
        """
        Return the last n rows

        Parameters
        ----------
        n: int
        
        Returns
        -------
        DataFrame
        """
        tail_dict = {}
        for key, value in self._data.items():
        	tail_dict[key] = value[-n:]

        return DataFrame(tail_dict)

    #### Aggregation Methods ####

    def min(self):
        return self._agg(np.min)

    def max(self):
        return self._agg(np.max)

    def mean(self):
        return self._agg(np.mean)

    def median(self):
        return self._agg(np.median)

    def sum(self):
        return self._agg(np.sum)

    def var(self):
        return self._agg(np.var)

    def std(self):
        return self._agg(np.std)

    def all(self):
        return self._agg(np.all)

    def any(self):
        return self._agg(np.any)

    def argmax(self):
        return self._agg(np.argmax)

    def argmin(self):
        return self._agg(np.argmin)

    def _agg(self, aggfunc):
        """
        Generic aggregation function that applies the
        aggregation to each column

        Parameters
        ----------
        aggfunc: str of the aggregation function name in NumPy
        
        Returns
        -------
        A DataFrame
        """
        agg_dict = {}
        for key, values in self._data.items():
        	try:
        		val = aggfunc(values)
        	except TypeError:
        		continue
        	agg_dict[key] = np.array([val])
        return DataFrame(agg_dict)

    def isna(self):
        """
        Determines whether each value in the DataFrame is missing or not

        Returns
        -------
        A DataFrame of booleans the same size as the calling DataFrame
        """
        nan_dict = {}
        for key, value in self._data.items():
        	if (value.dtype.kind == 'O') | (value.dtype.kind == 'U'):
        		nan_dict[key] = value == None
        	else:
        		nan_dict[key] = np.isnan(value)

        return DataFrame(nan_dict)

    def count(self):
        """
        Counts the number of non-missing values per column

        Returns
        -------
        A DataFrame
        """
        count_dict = {}
        for key,value in self.isna()._data.items():
        	counter = 0
        	for val in value:
        		if not val:
        			counter += 1
        	count_dict[key] = np.array([counter])

        return DataFrame(count_dict)

    def unique(self):
        """
        Finds the unique values of each column

        Returns
        -------
        A list of one-column DataFrames
        """
        unique_list = []
        for key, value in self._data.items():
            unique_dict = {}
            unique_dict[key] = np.unique(value)
            unique_list.append(DataFrame(unique_dict))

        return unique_list

    def nunique(self):
        """
        Find the number of unique values in each column

        Returns
        -------
        A DataFrame
        """
        nunique_dict = {}
        for key, value in self._data.items():
            nunique_dict[key] = np.array(len(np.unique(value)))

        return DataFrame(nunique_dict)

    def value_counts(self, normalize=False):
        """
        Returns the frequency of each unique value for each column

        Parameters
        ----------
        normalize: bool
            If True, returns the relative frequencies (percent)

        Returns
        -------
        A list of DataFrames or a single DataFrame if one column
        """
        value_list = []
        for key, value in self._data.items():
            value_dict = {}
            # find the keys and values
            keys, vals = np.unique(value, return_counts = True)

            # find unique keys
            keys = np.unique(keys)

            # sort the values according to frequency
            # in the descending order
            order = np.argsort(-vals)
            vals = vals[order]
            keys = keys[order]

            if normalize:
                vals = vals / vals.sum()

            value_dict[key] = keys
            value_dict['count'] = vals

            value_list.append(DataFrame(value_dict))
        return value_list

    def rename(self, columns):
        """
        Renames columns in the DataFrame

        Parameters
        ----------
        columns: dict
            A dictionary mapping the old column name to the new column name
        
        Returns
        -------
        A DataFrame
        """
        renamed_dict = {}
        if not isinstance(columns, dict):
            raise TypeError("'cols' must be a dictionary")

        for key, value in self._data.items():
            if key in columns:
                new_key = columns[key]
                renamed_dict[new_key] = value
            else:
                renamed_dict[key] = value

        return DataFrame(renamed_dict)

    def drop(self, columns):
        """
        Drops one or more columns from a DataFrame

        Parameters
        ----------
        columns: str or list of strings

        Returns
        -------
        A DataFrame
        """
        if not isinstance(columns, (str, list)):
            raise TypeError("'columns' should be a list or string")

        dropped_dict = {}
        for key, value in self._data.items():
            if key in columns:
                continue
            else:
                dropped_dict[key] = value

        return DataFrame(dropped_dict)

    #### Non-Aggregation Methods ####

    def abs(self):
        """
        Takes the absolute value of each value in the DataFrame

        Returns
        -------
        A DataFrame
        """
        return self._non_agg(np.abs)

    def cummin(self):
        """
        Finds cumulative minimum by column

        Returns
        -------
        A DataFrame
        """
        return self._non_agg(np.minimum.accumulate)

    def cummax(self):
        """
        Finds cumulative maximum by column

        Returns
        -------
        A DataFrame
        """
        return self._non_agg(np.maximum.accumulate)

    def cumsum(self):
        """
        Finds cumulative sum by column

        Returns
        -------
        A DataFrame
        """
        return self._non_agg(np.cumsum)

    def clip(self, lower=None, upper=None):
        """
        All values less than lower will be set to lower
        All values greater than upper will be set to upper

        Parameters
        ----------
        lower: number or None
        upper: number or None

        Returns
        -------
        A DataFrame
        """
        return self._non_agg(np.clip, a_min=lower, a_max=upper)

    def round(self, n):
        """
        Rounds values to the nearest n decimals

        Returns
        -------
        A DataFrame
        """
        return self._non_agg(np.round, decimals=n)

    def copy(self):
        """
        Copies the DataFrame

        Returns
        -------
        A DataFrame
        """
        return self._non_agg(np.copy)

    def _non_agg(self, funcname, **kwargs):
        """
        Generic non-aggregation function
    
        Parameters
        ----------
        funcname: numpy function
        kwargs: extra keyword arguments for certain functions

        Returns
        -------
        A DataFrame
        """
        pass

    def diff(self, n=1):
        """
        Take the difference between the current value and
        the nth value above it.

        Parameters
        ----------
        n: int

        Returns
        -------
        A DataFrame
        """
        def func():
            pass
        return self._non_agg(func)

    def pct_change(self, n=1):
        """
        Take the percentage difference between the current value and
        the nth value above it.

        Parameters
        ----------
        n: int

        Returns
        -------
        A DataFrame
        """
        def func():
            pass
        return self._non_agg(func)

    #### Arithmetic and Comparison Operators ####

    def __add__(self, other):
        return self._oper('__add__', other)

    def __radd__(self, other):
        return self._oper('__radd__', other)

    def __sub__(self, other):
        return self._oper('__sub__', other)

    def __rsub__(self, other):
        return self._oper('__rsub__', other)

    def __mul__(self, other):
        return self._oper('__mul__', other)

    def __rmul__(self, other):
        return self._oper('__rmul__', other)

    def __truediv__(self, other):
        return self._oper('__truediv__', other)

    def __rtruediv__(self, other):
        return self._oper('__rtruediv__', other)

    def __floordiv__(self, other):
        return self._oper('__floordiv__', other)

    def __rfloordiv__(self, other):
        return self._oper('__rfloordiv__', other)

    def __pow__(self, other):
        return self._oper('__pow__', other)

    def __rpow__(self, other):
        return self._oper('__rpow__', other)

    def __gt__(self, other):
        return self._oper('__gt__', other)

    def __lt__(self, other):
        return self._oper('__lt__', other)

    def __ge__(self, other):
        return self._oper('__ge__', other)

    def __le__(self, other):
        return self._oper('__le__', other)

    def __ne__(self, other):
        return self._oper('__ne__', other)

    def __eq__(self, other):
        return self._oper('__eq__', other)

    def _oper(self, op, other):
        """
        Generic operator function

        Parameters
        ----------
        op: str name of special method
        other: the other object being operated on

        Returns
        -------
        A DataFrame
        """
        pass

    def sort_values(self, by, asc=True):
        """
        Sort the DataFrame by one or more values

        Parameters
        ----------
        by: str or list of column names
        asc: boolean of sorting order

        Returns
        -------
        A DataFrame
        """
        pass

    def sample(self, n=None, frac=None, replace=False, seed=None):
        """
        Randomly samples rows the DataFrame

        Parameters
        ----------
        n: int
            number of rows to return
        frac: float
            Proportion of the data to sample
        replace: bool
            Whether or not to sample with replacement
        seed: int
            Seeds the random number generator

        Returns
        -------
        A DataFrame
        """
        pass

    def pivot_table(self, rows=None, columns=None, values=None, aggfunc=None):
        """
        Creates a pivot table from one or two 'grouping' columns.

        Parameters
        ----------
        rows: str of column name to group by
            Optional
        columns: str of column name to group by
            Optional
        values: str of column name to aggregate
            Required
        aggfunc: str of aggregation function

        Returns
        -------
        A DataFrame
        """
        pass

    def _add_docs(self):
        agg_names = ['min', 'max', 'mean', 'median', 'sum', 'var',
                     'std', 'any', 'all', 'argmax', 'argmin']
        agg_doc = \
        """
        Find the {} of each column
        
        Returns
        -------
        DataFrame
        """
        for name in agg_names:
            getattr(DataFrame, name).__doc__ = agg_doc.format(name)


class StringMethods:

    def __init__(self, df):
        self._df = df

    def capitalize(self, col):
        return self._str_method(str.capitalize, col)

    def center(self, col, width, fillchar=None):
        if fillchar is None:
            fillchar = ' '
        return self._str_method(str.center, col, width, fillchar)

    def count(self, col, sub, start=None, stop=None):
        return self._str_method(str.count, col, sub, start, stop)

    def endswith(self, col, suffix, start=None, stop=None):
        return self._str_method(str.endswith, col, suffix, start, stop)

    def startswith(self, col, suffix, start=None, stop=None):
        return self._str_method(str.startswith, col, suffix, start, stop)

    def find(self, col, sub, start=None, stop=None):
        return self._str_method(str.find, col, sub, start, stop)

    def len(self, col):
        return self._str_method(str.__len__, col)

    def get(self, col, item):
        return self._str_method(str.__getitem__, col, item)

    def index(self, col, sub, start=None, stop=None):
        return self._str_method(str.index, col, sub, start, stop)

    def isalnum(self, col):
        return self._str_method(str.isalnum, col)

    def isalpha(self, col):
        return self._str_method(str.isalpha, col)

    def isdecimal(self, col):
        return self._str_method(str.isdecimal, col)

    def islower(self, col):
        return self._str_method(str.islower, col)

    def isnumeric(self, col):
        return self._str_method(str.isnumeric, col)

    def isspace(self, col):
        return self._str_method(str.isspace, col)

    def istitle(self, col):
        return self._str_method(str.istitle, col)

    def isupper(self, col):
        return self._str_method(str.isupper, col)

    def lstrip(self, col, chars):
        return self._str_method(str.lstrip, col, chars)

    def rstrip(self, col, chars):
        return self._str_method(str.rstrip, col, chars)

    def strip(self, col, chars):
        return self._str_method(str.strip, col, chars)

    def replace(self, col, old, new, count=None):
        if count is None:
            count = -1
        return self._str_method(str.replace, col, old, new, count)

    def swapcase(self, col):
        return self._str_method(str.swapcase, col)

    def title(self, col):
        return self._str_method(str.title, col)

    def lower(self, col):
        return self._str_method(str.lower, col)

    def upper(self, col):
        return self._str_method(str.upper, col)

    def zfill(self, col, width):
        return self._str_method(str.zfill, col, width)

    def encode(self, col, encoding='utf-8', errors='strict'):
        return self._str_method(str.encode, col, encoding, errors)

    def _str_method(self, method, col, *args):
        pass


def read_csv(fn):
    """
    Read in a comma-separated value file as a DataFrame

    Parameters
    ----------
    fn: string of file location

    Returns
    -------
    A DataFrame
    """
    pass
