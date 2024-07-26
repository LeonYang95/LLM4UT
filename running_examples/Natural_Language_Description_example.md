You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.
### Instruction:
This is the method that you are going to test.
```
public void removeColumn(Comparable columnKey) {
    if (columnKey == null) {
        throw new IllegalArgumentException("Null 'columnKey' argument.");
    }
    if (!this.columnKeys.contains(columnKey)) {
        throw new UnknownKeyException("Unknown key: " + columnKey);
    }
    Iterator iterator = this.rows.iterator();
    while (iterator.hasNext()) {
        DefaultKeyedValues rowData = (DefaultKeyedValues) iterator.next();
        int index = rowData.getIndex(columnKey);
        if (index >= 0) {
            rowData.removeValue(columnKey);
        }
    }
    this.columnKeys.remove(columnKey);
}
```
The parameter of the method is `columnKey`.
The parameters come from class `Comparable`.
The focal method belongs to the class `org.jfree.data.DefaultKeyedValues2D`, and the constructors are:
```
 public DefaultKeyedValues2D(boolean sortRowKeys);
public DefaultKeyedValues2D(); 
```
These are the fields defined in the class:
```
private static final long serialVersionUID = -5514169970951994748L;
private List rowKeys;
private List columnKeys;
private List rows;
private boolean sortRowKeys;
```
These are the methods defined in the class :
```
public Comparable getColumnKey(int column);
public void addValue(Number value, Comparable rowKey, Comparable columnKey);
public Number getValue(int row, int column);
public DefaultKeyedValues2D(boolean sortRowKeys);
public List getRowKeys();
public int getRowCount();
public void removeValue(Comparable rowKey, Comparable columnKey);
public int hashCode();
public Number getValue(Comparable rowKey, Comparable columnKey);
public List getColumnKeys();
public void setValue(Number value, Comparable rowKey, Comparable columnKey);
public void removeColumn(int columnIndex);
public void removeRow(int rowIndex);
public int getColumnCount();
public void clear();
public boolean equals(Object o);
public int getColumnIndex(Comparable key);
public Object clone() throws CloneNotSupportedException;
public int getRowIndex(Comparable key);
public void removeRow(Comparable rowKey);
public DefaultKeyedValues2D();
public Comparable getRowKey(int row);
```
Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.
### Response:
```java
import org.junit.Test;
import org.junit.Assert;
import org.junit.Before;
import org.junit.After; 
import org.junit.Assert.*;
import org.junit.Ignore;
import org.junit.BeforeClass;
import org.junit.AfterClass;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.junit.Rule;
import org.junit.rules.ExpectedException;
import org.mockito.Mockito.*
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import java.io.Serializable;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import org.jfree.chart.util.ObjectUtilities;
import org.jfree.chart.util.PublicCloneable;

public class DefaultKeyedValues2DTest{

    private DefaultKeyedValues2D defaultKeyedValues2D;

    @Before
    public void setUp() {
        defaultKeyedValues2D = new DefaultKeyedValues2D();
    }

    @After
    public void tearDown() {
        defaultKeyedValues2D = null;
    }

    @Test
    public void testRemoveColumn_NullColumnKey() {
        expectedEx.expect(IllegalArgumentException.class);
        expectedEx.expectMessage("Null 'columnKey' argument.");
        defaultKeyedValues2D.removeColumn(null);
    }

    @Test
    public void testRemoveColumn_UnknownColumnKey() {
        expectedEx.expect(UnknownKeyException.class);
        expectedEx.expectMessage("Unknown key: unknownKey");
        defaultKeyedValues2D.removeColumn("unknownKey");
    }

    @Test
    public void testRemoveColumn_ValidColumnKey() {
        Comparable columnKey = "columnKey";
        defaultKeyedValues2D.addValue(1, "rowKey", columnKey);
        defaultKeyedValues2D.removeColumn(columnKey);
        assertThat(defaultKeyedValues2D.getColumnKeys(), not(hasItem(columnKey)));
    }

    @Test
    public void testRemoveColumn_ColumnKeyInRows() {
        Comparable columnKey = "columnKey";
        defaultKeyedValues2D.addValue(1, "rowKey", columnKey);
        defaultKeyedValues2D.removeColumn(columnKey);
        assertThat(defaultKeyedValues2D.getRowKeys(), not(hasItem(columnKey)));
    }

    @Test
    public void testRemoveColumn_ColumnKeyNotInRows() {
        Comparable columnKey = "columnKey";
        defaultKeyedValues2D.addValue(1, "rowKey", columnKey);
        defaultKeyedValues2D.removeColumn(columnKey);
        assertThat(defaultKeyedValues2D.getRowKeys(), not(hasItem(columnKey)));
    }
}